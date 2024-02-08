"""
This chart displays the period each year between the first and last SPC/WPC
outlook type for a given NWS forecast office, state or county.
The dates presented
are the commonly considered date of outlook being valid for.  Technically,
the outlooks end at 12 UTC of the following day.</p>

<p>If you select the "View by Contiguous US" option, there is no spatial
overlay check possible at this time.</p>

<p>An option exists to threshold the amount of spatial overlap between the
outlook geometry and the NWS forecast office or state.  This is useful for
the situation of avoiding sliver touches or overlaps that aren't of perhaps
significance.  There is an "engulfs" option, that requires a 99% overlap. A
100% overlap is difficult for certain situations and this may generally be
difficult for offices that have marine zones.</p>

<p>Autoplot <a href="/plotting/auto/?q=200">200</a> is similar, but generates
spatial heatmaps.</p>
"""
import calendar
import datetime

import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MaxNLocator
from pyiem import reference
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {
    "0": "At least touches",
    "5": "At least 5% overlap",
    "50": "At least 50% overlap",
    "99": "Engulfs",
}
PDICT2 = {
    "conus": "View by Contiguous US",
    "wfo": "View by Single NWS Forecast Office",
    "state": "View by State",
    "ugc": "View by Selected County/Zone",
}
PDICT3 = {
    "C": "SPC Convective Outlook",
    "F": "SPC Fire Weather Outlook",
    "E": "WPC Excessive Rainfall Outlook",
}
PDICT4 = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
}
OUTLOOKS = {
    "ANY SEVERE.0.02": "Any Severe 2% (Day 3+)",
    "ANY SEVERE.0.05": "Any Severe 5% (Day 3+)",
    "ANY SEVERE.0.15": "Any Severe 15% (Day 3+)",
    "ANY SEVERE.0.25": "Any Severe 25% (Day 3+)",
    "ANY SEVERE.0.30": "Any Severe 30% (Day 3+)",
    "ANY SEVERE.0.35": "Any Severe 35% (Day 3+)",
    "ANY SEVERE.0.45": "Any Severe 45% (Day 3+)",
    "ANY SEVERE.0.60": "Any Severe 60% (Day 3+)",
    "ANY SEVERE.SIGN": "Any Severe Significant (Day 3+)",
    "CATEGORICAL.TSTM": "Categorical Thunderstorm Risk",
    "CATEGORICAL.MRGL": "Categorical Marginal Risk (2015+)",
    "CATEGORICAL.SLGT": "Categorical Slight Risk",
    "CATEGORICAL.ENH": "Categorical Enhanced Risk (2015+)",
    "CATEGORICAL.MDT": "Categorical Moderate Risk",
    "CATEGORICAL.HIGH": "Categorical High Risk",
    "FIRE WEATHER CATEGORICAL.CRIT": "Categorical Critical Fire Wx (Days 1-2)",
    "FIRE WEATHER CATEGORICAL.EXTM": "Categorical Extreme Fire Wx (Days 1-2)",
    "CRITICAL FIRE WEATHER AREA.0.15": (
        "Critical Fire Weather Area 15% (Days3-7)"
    ),
    "HAIL.0.05": "Hail 5% (Days 1+2)",
    "HAIL.0.15": "Hail 15% (Days 1+2)",
    "HAIL.0.25": "Hail 25% (Days 1+2)",
    "HAIL.0.30": "Hail 30% (Days 1+2)",
    "HAIL.0.35": "Hail 35% (Days 1+2)",
    "HAIL.0.45": "Hail 45% (Days 1+2)",
    "HAIL.0.60": "Hail 60% (Days 1+2)",
    "HAIL.SIGN": "Hail Significant (Days 1+2)",
    "TORNADO.0.02": "Tornado 2% (Days 1+2)",
    "TORNADO.0.05": "Tornado 5% (Days 1+2)",
    "TORNADO.0.10": "Tornado 10% (Days 1+2)",
    "TORNADO.0.15": "Tornado 15% (Days 1+2)",
    "TORNADO.0.25": "Tornado 25% (Days 1+2)",
    "TORNADO.0.30": "Tornado 30% (Days 1+2)",
    "TORNADO.0.35": "Tornado 35% (Days 1+2)",
    "TORNADO.0.45": "Tornado 45% (Days 1+2)",
    "TORNADO.0.60": "Tornado 60% (Days 1+2)",
    "TORNADO.SIGN": "Tornado Significant (Days 1+2)",
    "WIND.0.05": "Wind 5% (Days 1+2)",
    "WIND.0.15": "Wind 15% (Days 1+2)",
    "WIND.0.25": "Wind 25% (Days 1+2)",
    "WIND.0.30": "Wind 30% (Days 1+2)",
    "WIND.0.35": "Wind 35% (Days 1+2)",
    "WIND.0.45": "Wind 45% (Days 1+2)",
    "WIND.0.60": "Wind 60% (Days 1+2)",
    "WIND.SIGN": "Wind Significant (Days 1+2)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        {
            "type": "year",
            "name": "year",
            "default": 1986,
            "label": "Start Year of Plot:",
            "min": 1986,
        },
        {
            "type": "select",
            "options": PDICT3,
            "default": "c",
            "label": "Select Outlook Type:",
            "name": "outlook_type",
        },
        {
            "type": "select",
            "options": OUTLOOKS,
            "default": "CATEGORICAL.SLGT",
            "label": "Select Outlook Threshold:",
            "name": "threshold",
        },
        {
            "type": "select",
            "options": PDICT4,
            "default": "1",
            "label": "Select Day:",
            "name": "day",
        },
        dict(
            type="select",
            name="opt",
            default="wfo",
            options=PDICT2,
            label="View by WFO, State or Zone?",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(type="state", default="IA", name="state", label="Select State:"),
        {
            "type": "ugc",
            "name": "ugc",
            "default": "IAZ048",
            "label": "Select County/Zone:",
        },
        {
            "type": "select",
            "options": PDICT,
            "default": "0",
            "label": (
                "Select Spatial Overlap Threshold:<br />"
                "<i>Warning: overlap percentage adds 10s of "
                "seconds to plot generation</i>"
            ),
            "name": "overlap",
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    wfo = ctx["wfo"][:4]
    opt = ctx["opt"]
    overlap = ctx["overlap"]
    state = ctx["state"]
    ugc = ctx["ugc"]
    (category, threshold) = ctx["threshold"].split(".", 1)

    params = {
        "wfo": wfo,
        "state": state,
        "overlap": int(overlap) / 100.0,
        "threshold": threshold,
        "category": category,
        "day": ctx["day"],
        "ugc": ugc,
        "sts": datetime.date(ctx["year"], 1, 1),
        "outlook_type": ctx["outlook_type"].upper(),
    }
    geomtable = "cwa"
    limiter = "g.wfo = :wfo"
    geomcol = "the_geom"
    ugcname = ""
    if opt == "wfo":
        geomtable = "states"
        limiter = "g.state_abbr = :state"
    elif opt == "ugc":
        geomtable = "ugcs"
        limiter = "g.ugc = :ugc and end_ts is null"
        geomcol = "geom"
        pgconn, cursor = get_dbconnc("postgis")
        cursor.execute(
            "select name from ugcs where ugc = %s and end_ts is null",
            (ugc,),
        )
        ugcname = cursor.fetchone()["name"]
        cursor.close()
        pgconn.close()
    overlapsql = ""
    if overlap != "0":
        overlapsql = (
            f"and ST_Area(ST_Intersection(o.geom, g.{geomcol})::geography) / "
            f"(select ST_Area({geomcol}::geography) from {geomtable} g "
            f"where {limiter}) > :overlap"
        )
    with get_sqlalchemy_conn("postgis") as conn:
        if opt == "conus":
            df = pd.read_sql(
                text(
                    """
                select distinct date(expire - '12 hours'::interval) as date
                from spc_outlooks o WHERE o.outlook_type = :outlook_type and
                o.day = :day
                and o.threshold = :threshold and o.category = :category and
                o.expire > :sts
                """
                ),
                conn,
                params=params,
                index_col=None,
                parse_dates="date",
            )

        else:
            df = pd.read_sql(
                text(
                    f"""
                select distinct date(expire - '12 hours'::interval) as date
                from spc_outlooks o, {geomtable} g WHERE {limiter}
                and o.outlook_type = :outlook_type and o.day = :day
                and o.threshold = :threshold and o.category = :category and
                ST_Intersects(o.geom, g.{geomcol}) {overlapsql} and
                o.expire > :sts
                """
                ),
                conn,
                params=params,
                index_col=None,
                parse_dates="date",
            )
    if df.empty:
        raise NoDataFound("No data found for query")
    df["doy"] = df["date"].dt.dayofyear
    df["year"] = df["date"].dt.year

    tt = OUTLOOKS[ctx["threshold"]].split("(")[0].strip()
    title = (
        f"{'WPC' if ctx['outlook_type'] == 'E' else 'SPC'} Day "
        f"{ctx['day']} {tt} Outlook"
    )
    verb = "Intersects" if overlap != "99" else "Engulfs"
    subtitle = (
        f"Based on Unofficial IEM Archives, {verb} [{wfo}] "
        f"NWS {ctx['_nt'].sts[wfo]['name']} CWA"
    )
    if opt == "state":
        subtitle = f"{verb} State of {reference.state_names[state]}"
    elif opt == "ugc":
        subtitle = f"{verb} County/Zone {ugcname} [{ugc}]"
    elif opt == "conus":
        subtitle = "Based on Unofficial IEM Archives, Contiguous US"
    if ctx["overlap"] not in ["0", "99"]:
        subtitle += f" with >= {overlap}% overlap"
    fig = figure(apctx=ctx, title=title, subtitle=subtitle)
    ax = fig.add_axes([0.08, 0.1, 0.58, 0.8])
    monofont = FontProperties(family="monospace")
    for year, gdf in df.groupby("year"):
        size = max(gdf["doy"].max() - gdf["doy"].min(), 1)
        ax.barh(
            year,
            size,
            left=gdf["doy"].min(),
            ec="brown",
            fc="tan",
            align="center",
        )
        ax.barh(
            gdf["year"].values,
            [1] * len(gdf.index),
            left=gdf["doy"].values,
            zorder=3,
            color="r",
        )
        # Add a label for the year on the RHS of ax
        ax.annotate(
            f"{gdf['date'].min():%b %d} - {gdf['date'].max():%b %d, %Y}",
            xy=(1.01, year),
            xycoords=("axes fraction", "data"),
            va="center",
            ha="left",
            color="k",
            fontproperties=monofont,
        )
    gdf = df[["year", "doy"]].groupby("year").agg(["min", "max"])
    if len(gdf.index) > 2:
        # Exclude first and last year in the average
        avg_start = np.average(gdf["doy", "min"].values[1:-1])
        avg_end = np.average(gdf["doy", "max"].values[1:-1])
        ax.axvline(avg_start, ls=":", lw=2, color="k")
        ax.axvline(avg_end, ls=":", lw=2, color="k")
        x0 = datetime.date(2000, 1, 1)
        _1 = (x0 + datetime.timedelta(days=int(avg_start))).strftime("%-d %b")
        _2 = (x0 + datetime.timedelta(days=int(avg_end))).strftime("%-d %b")
        ax.set_xlabel(f"Average Start Date: {_1}, End Date: {_2}")
    ax.grid()
    xticks = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(1, 367)
    ax.set_ylabel("Year")
    ax.set_ylim(df["year"].min() - 0.5, df["year"].max() + 0.5)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # __________________________________________
    ax = fig.add_axes([0.86, 0.1, 0.1, 0.8])
    gdf = df[["year", "doy"]].groupby("year").count()
    ax.barh(gdf.index.values, gdf["doy"].values, fc="blue", align="center")
    for year, val in zip(gdf.index.values, gdf["doy"].values):
        ax.annotate(
            f"{val}",
            xy=(1.01, year),
            xycoords=("axes fraction", "data"),
            va="center",
            ha="left",
            fontproperties=monofont,
        )
    ax.set_ylim(df["year"].min() - 0.5, df["year"].max() + 0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Days")
    ax.xaxis.set_major_locator(MaxNLocator(3, integer=True))

    return fig, df


if __name__ == "__main__":
    plotter({"opt": "state", "state": "OK"})
