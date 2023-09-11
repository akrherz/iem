"""
This table presents the extreme hourly value of
some variable of your choice based on available observations maintained
by the IEM.  Sadly, this app will likely point out some bad data points
as such points tend to be obvious at extremes.  If you contact us to
point out troubles, we'll certainly attempt to fix the archive to
remove the bad data points.</p>

<p>For non-precipitation reports, observations are arbitrarly bumped 10
minutes into the future to place the near to top of the hour obs on
that hour.  For example, a 9:53 AM observation becomes the ob for 10 AM.
"""
import datetime

import pandas as pd
from matplotlib.font_manager import FontProperties
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

PDICT = {
    "max_dwpf": "Highest Dew Point Temperature",
    "min_dwpf": "Lowest Dew Point Temperature",
    "max_tmpf": "Highest Air Temperature",
    "min_tmpf": "Lowest Air Temperature",
    "max_feel": "Highest Feels Like Temperature",
    "min_feel": "Lowest Feels Like Temperature",
    "max_p01i": "Maximum Hourly Precipitation",
    "max_mslp": "Maximum Sea Level Pressure",
    "min_mslp": "Minimum Sea Level Pressure",
    "max_alti": "Maximum Pressure Altimeter",
    "min_alti": "Minimum Pressure Altimeter",
}
UNITS = {
    "max_dwpf": "F",
    "max_tmpf": "F",
    "min_dwpf": "F",
    "min_tmpf": "F",
    "min_feel": "F",
    "max_feel": "F",
    "max_p01i": "in",
    "max_mslp": "mb",
    "min_mslp": "mb",
    "max_alti": "in",
    "min_alti": "in",
}
MDICT = {
    "all": "No Month Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "gs": "1 May to 30 Sep",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            options=MDICT,
            label="Select Month/Season/All",
        ),
        dict(
            type="sday",
            optional=True,
            name="sday",
            label="Start Day of The Year (inclusive):",
            default=f"{datetime.date.today():%m%d}",
        ),
        dict(
            type="sday",
            optional=True,
            name="eday",
            label="End Day of The Year (inclusive):",
            default="1231",
        ),
        dict(
            type="select",
            name="var",
            options=PDICT,
            default="max_dwpf",
            label="Which Variable to Plot",
        ),
    ]
    return desc


def rounder(row, varname):
    """Hacky."""
    if varname in ["max_p01i", "max_alti", "min_alti"]:
        return f"{row[varname]:.2f}"
    return f"{row[varname]:3.0f}"


def plotter(fdict):
    """Go"""
    font0 = FontProperties()
    font0.set_family("monospace")
    font0.set_size(16)
    font1 = FontProperties()
    font1.set_size(16)

    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx["var"]
    varname2 = varname.split("_")[1]
    if varname2 in ["dwpf", "tmpf", "feel"]:
        varname2 = "i" + varname2
    month = ctx["month"]
    station = ctx["zstation"]

    if month == "all":
        months = list(range(1, 13))
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "gs":
        months = [5, 6, 7, 8, 9]
    else:
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]
    params = {
        "tzname": ctx["_nt"].sts[station]["tzname"],
        "station": station,
        "months": months,
    }
    doylimiter = ""
    monlimiter = ""
    if "sday" in ctx and "eday" in ctx:
        params["sday"] = f"{ctx['sday']:%m%d}"
        params["eday"] = f"{ctx['eday']:%m%d}"
        op = "and" if params["sday"] < params["eday"] else "or"
        doylimiter = (
            f"and (to_char(valid at time zone :tzname, 'mmdd') >= :sday {op} "
            "to_char(valid at time zone :tzname, 'mmdd') <= :eday)"
        )
        over = f"{ctx['sday']:%-d %b} thru {ctx['eday']:%-d %b}"
    else:
        over = MDICT[month]
        if len(months) < 12:
            monlimiter = (
                "and extract(month from valid at time zone :tzname) "
                "= ANY(:months)"
            )
    delta = 10 if varname != "max_p01i" else -1
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                f"""
        WITH obs as (
            SELECT (valid + '{delta} minutes'::interval)
                at time zone :tzname as ts,
            tmpf::int as itmpf, dwpf::int as idwpf,
            feel::int as ifeel, mslp, alti, p01i from alldata
            where station = :station {doylimiter} {monlimiter}
            ),
        agg1 as (
            SELECT extract(hour from ts) as hr,
            max(idwpf) as max_dwpf,
            max(itmpf) as max_tmpf,
            min(idwpf) as min_dwpf,
            min(itmpf) as min_tmpf,
            min(ifeel) as min_feel,
            max(ifeel) as max_feel,
            max(alti) as max_alti,
            min(alti) as min_alti,
            max(mslp) as max_mslp,
            min(mslp) as min_mslp,
            max(p01i) as max_p01i
            from obs GROUP by hr)
        SELECT o.ts, a.hr::int as hr,
            a.{varname} from agg1 a JOIN obs o on
            (a.hr = extract(hour from o.ts)
            and a.{varname} = o.{varname2})
            ORDER by a.hr ASC, o.ts DESC
        """
            ),
            conn,
            params=params,
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data was found.")
    y0 = 0.1
    yheight = 0.8
    dy = yheight / 24.0
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata")
    title = (
        f"{ctx['_sname']} ({ab.year}-{datetime.date.today().year})\n"
        f"{PDICT[varname]} [{over}]"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    ax.set_position([0.12, y0, 0.57, yheight])
    ax.barh(df["hr"], df[varname], align="center")
    ax.set_ylim(-0.5, 23.5)
    ax.set_yticks([0, 4, 8, 12, 16, 20])
    ax.set_yticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    ax.grid(True)
    if varname == "max_p01i":
        ax.set_xlim([0, df[varname].max() + 0.5])
    else:
        delta = 0.25 if varname.find("alti") > -1 else 5
        ax.set_xlim([df[varname].min() - delta, df[varname].max() + delta])
    ax.set_ylabel(
        f"Local Time {ctx['_nt'].sts[station]['tzname']}",
        fontproperties=font1,
    )

    ypos = y0 + (dy / 2.0)
    for hr in range(24):
        sdf = df[df["hr"] == hr]
        if sdf.empty:
            continue
        row = sdf.iloc[0]
        fig.text(
            0.7,
            ypos,
            f"{rounder(row, varname):3s}: {pd.Timestamp(row['ts']):%d %b %Y}"
            f"{'*' if len(sdf.index) > 1 else ''}",
            fontproperties=font0,
            va="center",
        )
        ypos += dy
    ax.set_xlabel(
        f"{PDICT[varname]} {UNITS[varname]}, * denotes ties",
        fontproperties=font1,
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
