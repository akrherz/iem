"""
This chart presents a series of daily summary data
as a calendar.  The daily totals should be valid for the local day of the
weather station.  The climatology is based on the nearest NCEI 1981-2010
climate station, which in most cases is the same station.  Climatology
values are rounded to the nearest whole degree Fahrenheit and then compared
against the observed value to compute a departure.
"""
import datetime

import numpy as np
import pandas as pd
import psycopg2.extras
from matplotlib.patches import Rectangle
from pyiem.exceptions import NoDataFound
from pyiem.plot import calendar_plot
from pyiem.reference import TRACE_VALUE
from pyiem.util import (
    convert_value,
    get_autoplot_context,
    get_dbconn,
    get_sqlalchemy_conn,
)

PDICT = {
    "max_tmpf": "High Temperature",
    "high_departure": "High Temperature Departure",
    "min_tmpf": "Low Temperature",
    "low_departure": "Low Temperature Departure",
    "avg_tmpf": "Average Temperature",
    "avg_departure": "Average Temperature Departure",
    "max_dwpf": "Highest Dew Point Temperature",
    "min_dwpf": "Lowest Dew Point Temperature",
    "max_feel": "Maximum Feels Like Temperature",
    "min_feel": "Minimum Feels Like Temperature",
    "avg_smph": "Average Wind Speed [mph]",
    "max_smph": "Maximum Wind Speed/Gust [mph]",
    "pday": "Precipitation",
    "max_rstage": "Maximum Water Stage [ft]",
}
STAGES = "action flood moderate major".split()
COLORS = "white #ffff72 #ffc672 #ff7272 #e28eff".split()


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    m90 = today - datetime.timedelta(days=90)
    desc["arguments"] = [
        dict(
            type="sid",
            name="station",
            default="DSM",
            network="IA_ASOS",
            label="Select Station",
        ),
        dict(
            type="select",
            name="var",
            default="pday",
            label="Which Daily Variable:",
            options=PDICT,
        ),
        dict(
            type="date",
            name="sdate",
            default=m90.strftime("%Y/%m/%d"),
            label="Start Date:",
            min="1929/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End Date:",
            min="1929/01/01",
        ),
    ]
    return desc


def safe(row, varname):
    """Safe conversion of value for printing as a string"""
    val = row[varname]
    if val is None:
        return "M"
    if varname == "pday":
        if val == TRACE_VALUE:
            return "T"
        if val == 0:
            return "0"
        return f"{val:.2f}"
    if varname == "max_rstage":
        return f"{val:.2f}"
    # prevent -0 values
    return f"{int(val):.0f}"


def diff(val, climo):
    """Safe subtraction."""
    if val is None or climo is None:
        return 0
    return float(val) - climo


def add_stages_legend(fig, stagevals):
    """Add a stages legend."""
    handles = []
    labels = []
    for i, val in enumerate(stagevals[:-1]):
        if val is None:
            continue
        rect = Rectangle((0, 0), 1, 1, fc=COLORS[i + 1])
        handles.append(rect)
        labels.append(f"{STAGES[i]} {val}")
    if handles:
        fig.legend(handles, labels, ncol=4, loc=(0.4, 0.915))


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]

    # Get Climatology
    with get_sqlalchemy_conn("coop") as conn:
        cdf = pd.read_sql(
            "SELECT to_char(valid, 'mmdd') as sday, "
            "round(high::numeric, 0) as high, "
            "round(low::numeric, 0) as low, "
            "round(((high + low) / 2.)::numeric, 0) as avg, "
            "precip from ncei_climate91 WHERE station = %s ORDER by sday ASC",
            conn,
            params=(ctx["_nt"].sts[station]["ncei91"],),
            index_col="sday",
        )
    if cdf.empty:
        raise NoDataFound("No Data Found.")

    if ctx["network"].find("CLIMATE") > -1:
        cursor = get_dbconn("coop").cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cursor.execute(
            """
            SELECT
            day,
            high as max_tmpf,
            low as min_tmpf,
            null as max_dwpf,
            null as min_dwpf,
            null as max_feel,
            null as min_feel,
            (high + low) / 2. as avg_tmpf,
            precip as pday,
            null as avg_sknt, null as peak_wind,
            null as max_rstage
            from alldata
            WHERE day >= %s and day <= %s and
            station = %s ORDER by day ASC
        """,
            (sdate, edate, station),
        )
    else:
        pgconn = get_dbconn("iem")
        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            SELECT day, max_tmpf, min_tmpf, max_dwpf, min_dwpf,
            (max_tmpf + min_tmpf) / 2. as avg_tmpf,
            pday, avg_sknt, coalesce(max_gust, max_sknt) as peak_wind,
            max_rstage, max_feel, min_feel
            from summary s JOIN stations t
            on (t.iemid = s.iemid) WHERE s.day >= %s and s.day <= %s and
            t.id = %s and t.network = %s ORDER by day ASC
        """,
            (sdate, edate, station, ctx["network"]),
        )
    stagevals = []
    rows = []
    data = {}
    for row in cursor:
        hd = diff(row["max_tmpf"], cdf.at[row[0].strftime("%m%d"), "high"])
        ld = diff(row["min_tmpf"], cdf.at[row[0].strftime("%m%d"), "low"])
        ad = diff(row["avg_tmpf"], cdf.at[row[0].strftime("%m%d"), "avg"])
        avg_sknt = row["avg_sknt"]
        if avg_sknt is None:
            if varname == "avg_smph":
                continue
            avg_sknt = 0
        peak_wind = row["peak_wind"]
        if peak_wind is None:
            if varname == "max_smph":
                continue
            peak_wind = 0
        rows.append(
            dict(
                day=row["day"],
                max_tmpf=row["max_tmpf"],
                avg_smph=convert_value(avg_sknt, "knot", "mile / hour"),
                max_smph=convert_value(peak_wind, "knot", "mile / hour"),
                min_dwpf=row["min_dwpf"],
                max_dwpf=row["max_dwpf"],
                high_departure=hd,
                low_departure=ld,
                avg_departure=ad,
                min_tmpf=row["min_tmpf"],
                avg_tmpf=row["avg_tmpf"],
                min_feel=row["min_feel"],
                max_feel=row["max_feel"],
                pday=row["pday"],
                max_rstage=row["max_rstage"],
            )
        )
        data[row[0]] = {"val": safe(rows[-1], varname)}
        if data[row[0]]["val"] == "0":
            data[row[0]]["color"] = "k"
        elif varname == "high_departure":
            data[row[0]]["color"] = "b" if hd < 0 else "r"
        elif varname == "low_departure":
            data[row[0]]["color"] = "b" if ld < 0 else "r"
        elif varname == "avg_departure":
            data[row[0]]["color"] = "b" if ad < 0 else "r"
        elif varname == "max_rstage":
            if not stagevals:
                meta = ctx["_nt"].sts[station]
                stagevals = [meta[f"sigstage_{x}"] for x in STAGES]
                stagevals.append(1e9)
            if not pd.isna(row["max_rstage"]):
                idx = np.digitize(row["max_rstage"], stagevals)
                data[row[0]]["cellcolor"] = COLORS[idx]
    df = pd.DataFrame(rows)

    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']} "
        f"Daily {PDICT.get(varname)}"
    )
    subtitle = f"{sdate:%-d %b %Y} thru {edate:%-d %b %Y}"

    fig = calendar_plot(
        sdate,
        edate,
        data,
        title=title,
        subtitle=subtitle,
        apctx=ctx,
    )
    if varname == "max_rstage":
        add_stages_legend(fig, stagevals)
    return fig, df


if __name__ == "__main__":
    plotter({})
