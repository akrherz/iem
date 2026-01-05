"""
This chart presents a series of daily summary data
as a calendar.  The daily totals should be valid for the local day of the
weather station.  The climatology is based on the nearest NCEI 1991-2020
climate station, which in most cases is the same station.  Climatology
values are rounded to the nearest whole degree Fahrenheit and then compared
against the observed value to compute a departure.

<p>A current limitation is that no more than 12 months of data can be plotted
at a single time.  The image shape of the column plot is also hard coded as
well.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import calendar_plot, figure, get_cmap
from pyiem.reference import TRACE_VALUE, Z_OVERLAY2, Z_OVERLAY2_LABEL
from pyiem.util import convert_value

PDICT = {
    "max_tmpf": "High Temperature (°F)",
    "high_departure": "High Temperature Departure (°F)",
    "min_tmpf": "Low Temperature (°F)",
    "low_departure": "Low Temperature Departure (°F)",
    "avg_tmpf": "Average Temperature (°F)",
    "avg_departure": "Average Temperature Departure (°F)",
    "max_dwpf": "Highest Dew Point Temperature (°F)",
    "min_dwpf": "Lowest Dew Point Temperature (°F)",
    "max_feel": "Maximum Feels Like Temperature (°F)",
    "min_feel": "Minimum Feels Like Temperature (°F)",
    "avg_smph": "Average Wind Speed [mph]",
    "max_smph": "Maximum Wind Speed/Gust [mph]",
    "pday": "Precipitation [inch]",
    "max_rstage": "Maximum Water Stage [ft]",
}
BINS = {
    "max_tmpf": [-40, 121, 10],
    "high_departure": [-50, 51, 5],
    "min_tmpf": [-40, 91, 10],
    "low_departure": [-50, 51, 5],
    "avg_tmpf": [-20, 101, 5],
    "avg_departure": [-30, 31, 3],
    "max_dwpf": [-40, 91, 10],
    "min_dwpf": [-40, 91, 10],
    "max_feel": [-40, 121, 10],
    "min_feel": [-40, 121, 10],
    "avg_smph": [0, 51, 5],
    "max_smph": [0, 71, 5],
    "pday": [0, 3, 0.25],
    "max_rstage": [0, 51, 5],
}
LAYOUT = {
    "calendar": "Calendar Layout",
    "column": "Months as Columns Layout",
}
COLORIZE = {
    "yes": "Yes, colorize cells based on values",
    "no": "No, do not colorize cells",
}
STAGES = "action flood moderate major".split()
COLORS = "white #ffff72 #ffc672 #ff7272 #e28eff".split()


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 600}
    today = date.today()
    m90 = today - timedelta(days=90)
    desc["arguments"] = [
        dict(
            type="sid",
            name="station",
            default="DSM",
            network="IA_ASOS",
            label="Select Station",
            include_climodat=True,
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
            min="1900/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End Date:",
            min="1900/01/01",
        ),
        {
            "type": "select",
            "options": LAYOUT,
            "default": "calendar",
            "label": "Select calendar layout",
            "name": "layout",
        },
        {
            "type": "select",
            "options": COLORIZE,
            "default": "yes",
            "label": "Colorize cells?",
            "name": "colorize",
        },
        {
            "type": "cmap",
            "default": "jet",
            "name": "cmap",
            "label": "Select color ramp:",
        },
        {
            "type": "text",
            "label": (
                "Specify minimum, maximum, interval for color ramp bins "
                "as comma separated values (e.g. 0,101,10)"
            ),
            "default": "0,101,10",
            "optional": True,
            "name": "interval",
        },
    ]
    return desc


def column_plot(fig: Figure, sdate: date, edate: date, data: dict[date, dict]):
    """Create a specialized figure."""
    # Create an axes object to manually plot things onto
    ax = fig.add_axes((0.1, 0.1, 0.75, 0.8), frameon=False)
    ax.set_xlim(-0.5, 11.5)
    ax.set_xticks([])
    ax.set_yticks(np.arange(1, 32, 1))
    ax.set_yticklabels(np.arange(1, 32, 1))
    ax.set_ylim(31.5, -0.5)  # Invert y axis
    ax.set_ylabel("Day of Month")
    xpos = -1
    current_xmonth = -1
    for pdt in pd.date_range(sdate, edate):
        dt = pdt.date()
        if dt.month != current_xmonth:
            xpos += 1
            current_xmonth = dt.month
            ax.add_patch(
                Rectangle(
                    (xpos - 0.5, -0.5),
                    1,
                    1,
                    facecolor="white",
                    edgecolor="k",
                    lw=2,
                    zorder=Z_OVERLAY2_LABEL,  # Put overtop the days
                )
            )
            ax.annotate(
                dt.strftime("%b"),
                xy=(xpos, 0),
                ha="center",
                va="center",
                fontsize=12,
                zorder=Z_OVERLAY2_LABEL,
            )
        if dt not in data:
            continue
        val = data[dt]["val"]
        color = data[dt].get("color", "k")
        cellcolor = data[dt].get("cellcolor", "white")
        ax.add_patch(
            Rectangle(
                (xpos - 0.5, dt.day - 0.5),
                1,
                1,
                facecolor=cellcolor,
                edgecolor="lightgray",
                zorder=Z_OVERLAY2,
            )
        )
        ax.annotate(
            val,
            (xpos, dt.day),
            color=color,
            ha="center",
            va="center",
            fontsize=12,
            zorder=Z_OVERLAY2_LABEL,
        )


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


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    varname = ctx["var"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    # Check for more than 12 months of data
    if pd.date_range(sdate, edate).strftime("%Y%m").nunique() > 12:
        raise NoDataFound("Date range cannot exceed 12 months.")

    # Get Climatology
    with get_sqlalchemy_conn("coop") as conn:
        cdf = pd.read_sql(
            sql_helper("""SELECT to_char(valid, 'mmdd') as sday,
            round(high::numeric, 0) as high,
            round(low::numeric, 0) as low,
            round(((high + low) / 2.)::numeric, 0) as avg,
            precip from ncei_climate91 WHERE station = :ncei
            ORDER by sday ASC
            """),
            conn,
            params={"ncei": ctx["_nt"].sts[station]["ncei91"]},
            index_col="sday",
        )
    if cdf.empty:
        raise NoDataFound("No Data Found.")

    if ctx["network"].find("CLIMATE") > -1:
        with get_sqlalchemy_conn("coop") as conn:
            res = conn.execute(
                sql_helper("""
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
                WHERE day >= :sdate and day <= :edate and
                station = :station ORDER by day ASC
            """),
                {"sdate": sdate, "edate": edate, "station": station},
            )
    else:
        with get_sqlalchemy_conn("iem") as conn:
            res = conn.execute(
                sql_helper("""
                SELECT day, max_tmpf, min_tmpf, max_dwpf, min_dwpf,
                (max_tmpf + min_tmpf) / 2. as avg_tmpf,
                pday, avg_sknt, coalesce(max_gust, max_sknt) as peak_wind,
                max_rstage, max_feel, min_feel
            from summary s JOIN stations t
            on (t.iemid = s.iemid) WHERE s.day >= :sdate and s.day <= :edate
            and
            t.id = :station and t.network = :network ORDER by day ASC
        """),
                {
                    "sdate": sdate,
                    "edate": edate,
                    "station": station,
                    "network": ctx["network"],
                },
            )
    stagevals = []
    rows = []
    data = {}
    cmap = get_cmap(ctx["cmap"])
    if ctx.get("interval", "") != "":
        norm = BoundaryNorm(
            np.arange(*map(float, ctx["interval"].split(","))),
            cmap.N,
        )
    else:
        norm = BoundaryNorm(
            np.arange(*BINS[varname]),
            cmap.N,
        )
    for row in res.mappings():
        hd = diff(row["max_tmpf"], cdf.at[row["day"].strftime("%m%d"), "high"])
        ld = diff(row["min_tmpf"], cdf.at[row["day"].strftime("%m%d"), "low"])
        ad = diff(row["avg_tmpf"], cdf.at[row["day"].strftime("%m%d"), "avg"])
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
        data[row["day"]] = {"val": safe(rows[-1], varname)}
        if data[row["day"]]["val"] == "0":
            data[row["day"]]["color"] = "k"
        elif varname == "high_departure":
            data[row["day"]]["color"] = "b" if hd < 0 else "r"
        elif varname == "low_departure":
            data[row["day"]]["color"] = "b" if ld < 0 else "r"
        elif varname == "avg_departure":
            data[row["day"]]["color"] = "b" if ad < 0 else "r"
        elif varname == "max_rstage":
            if not stagevals:
                meta = ctx["_nt"].sts[station]
                stagevals = [meta[f"sigstage_{x}"] for x in STAGES]
                stagevals.append(1e9)
            if not pd.isna(row["max_rstage"]):
                idx = np.digitize(row["max_rstage"], stagevals)
                data[row["day"]]["cellcolor"] = COLORS[idx]
        if ctx["colorize"] == "yes":
            rawval = rows[-1][varname]
            if rawval is not None:
                color = cmap(norm([rawval]))[0]
                hexcolor = (
                    f"#{int(color[0] * 255):02x}{int(color[1] * 255):02x}"
                    f"{int(color[2] * 255):02x}"
                )
                data[row["day"]]["cellcolor"] = hexcolor
                # The text now needs to be in an opposite color, so to read!
                brightness = (
                    0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
                )
                data[row["day"]]["color"] = "k" if brightness > 0.5 else "w"

    df = pd.DataFrame(rows)

    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']} "
        f"Daily {PDICT.get(varname)}"
    )
    subtitle = f"{sdate:%-d %b %Y} thru {edate:%-d %b %Y}"

    if ctx["layout"] == "calendar":
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
    else:
        fig = figure(
            title=title,
            subtitle=subtitle,
            figsize=(8, 8),
        )
        column_plot(fig, sdate, edate, data)
        if ctx["colorize"] == "yes":
            # Create a ScalarMappable for the colorbar
            sm = ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])  # Required for ScalarMappable
            cax = fig.add_axes((0.9, 0.15, 0.02, 0.7))
            fig.colorbar(
                sm,
                cax=cax,
                orientation="vertical",
                label=PDICT.get(varname),
            )
    return fig, df
