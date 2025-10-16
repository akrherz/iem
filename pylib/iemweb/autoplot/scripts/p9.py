"""
This chart produces the daily climatology of
Degree Days for a location of your choice. Please note that
Feb 29 is not considered for this analysis.
"""

from datetime import date, datetime

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from sqlalchemy.engine import Connection

from iemweb.autoplot import ARG_STATION

PDICT = {
    "cdd": "Cooling Degree Days",
    "gdd": "Growing Degree Days",
    "hdd": "Heating Degree Days",
    "sdd": "Stress Degree Days",
}
PDICT2 = {
    "daily": "Daily Accumulated",
    "ytd": "Year to Date Accumulation",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    thisyear = date.today().year
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="year",
            name="year",
            default=thisyear,
            min=1893,
            label="Select Year:",
        ),
        {
            "type": "sday",
            "default": "0101",
            "name": "sday",
            "label": "Start Day of the Year for Plot",
        },
        {
            "type": "sday",
            "default": "1231",
            "name": "eday",
            "label": "Inclusive End Day of the Year for Plot",
        },
        dict(
            type="select",
            options=PDICT,
            default="gdd",
            name="var",
            label="Which variable to plot:",
        ),
        {
            "type": "select",
            "options": PDICT2,
            "label": "Plot Daily or YTD Accumulated?",
            "name": "w",
            "default": "daily",
        },
        dict(
            type="int",
            name="base",
            default="50",
            label="Enter CDD/GDD/HDD Base (F):",
        ),
        dict(
            type="int",
            name="ceiling",
            default="86",
            label="Enter GDD Ceiling / SDD Base (F):",
        ),
    ]
    return desc


@with_sqlalchemy_conn("coop")
def get_df(ctx: dict, conn: Connection | None = None) -> pd.DataFrame:
    """Compute things."""
    varname = ctx["var"]
    base = ctx["base"]
    ceiling = ctx["ceiling"]
    year = ctx["year"]
    glabel = f"{varname}{base}{ceiling}"

    gfunc = "gddxx(:base, :ceil, high, low)"
    if varname in ["hdd", "cdd"]:
        gfunc = f"{varname}(high, low, :base)"
    elif varname == "sdd":
        gfunc = "case when high > :ceil then high - :ceil else 0 end"

    obsdf = pd.read_sql(
        sql_helper(
            """SELECT year, sday, {gfunc} as {glabel} from alldata WHERE
        station = :sid and year > 1892 and sday != '0229'
        and sday >= :sday and sday <= :eday ORDER by day ASC
        """,
            gfunc=gfunc,
            glabel=glabel,
        ),
        conn,
        params={
            "sid": ctx["station"],
            "sday": f"{ctx['sday']:%m%d}",
            "eday": f"{ctx['eday']:%m%d}",
            "base": ctx["base"],
            "ceil": ctx["ceiling"],
        },
    )
    if obsdf.empty:
        raise NoDataFound("No data Found.")
    if ctx["w"] == "ytd":
        obsdf["accum"] = obsdf[["year", glabel]].groupby("year").cumsum()
        glabel = "accum"

    sdaydf = (
        obsdf[["sday", glabel]]
        .groupby("sday")
        .describe(percentiles=[0.05, 0.25, 0.75, 0.95])
    ).unstack(level=-1)

    # collapse the multi-index for columns
    retdf = sdaydf.reset_index().pivot(
        index="sday", columns="level_1", values=0
    )
    retdf[f"{year}{glabel}"] = obsdf[obsdf["year"] == year].set_index("sday")[
        glabel
    ]
    return retdf


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    thisyear = datetime.now().year
    year = ctx["year"]
    base = ctx["base"]
    ceiling = ctx["ceiling"]
    varname = ctx["var"]
    glabel = f"{varname}{base}{ceiling}"
    retdf = get_df(ctx)

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown Station Metadata.")
    syear = max(ab.year, 1893)

    title = f"base={base}/ceil={ceiling}"
    if varname in ["hdd", "cdd"]:
        title = f"base={base}"
    elif varname == "sdd":
        title = f"base={ceiling}"

    if ctx["w"] == "ytd":
        glabel = "accum"
    tt = f"{ctx['sday']:%-d %b} thru {ctx['eday']:%-d %b}"
    title = (
        f"({syear}-{thisyear}) [{tt}] {ctx['_sname']}\n"
        f"{year} {PDICT[varname]} ({title})"
    )
    # avoid leap year
    xaxis = pd.to_datetime(
        "2001" + retdf.reset_index()["sday"], format="%Y%m%d"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.plot(
        xaxis,
        retdf["mean"],
        color="r",
        zorder=2,
        lw=2.0,
        label="Average",
    )
    ax.scatter(
        pd.to_datetime("2001" + retdf.index, format="%Y%m%d"),
        retdf[f"{year}{glabel}"],
        color="b",
        zorder=2,
        label=f"{year}",
    )
    ax.bar(
        xaxis,
        retdf["95%"] - retdf["5%"],
        bottom=retdf["5%"],
        ec="tan",
        fc="tan",
        zorder=1,
        label="5-95 Percentile",
    )
    ax.bar(
        xaxis,
        retdf["75%"] - retdf["25%"],
        bottom=retdf["25%"],
        ec="lightblue",
        fc="lightblue",
        zorder=1,
        label="25-75 Percentile",
    )
    ax.set_xlim(xaxis.values[0], xaxis.values[-1])
    if varname == "gdd" and ctx["w"] == "daily":
        ax.set_ylim(-0.25, 40)
    ax.grid(True)
    ax.set_ylabel(f"{PDICT2[ctx['w']]} °F")
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-d %b"),
    )
    ax.legend(ncol=2)

    return fig, retdf
