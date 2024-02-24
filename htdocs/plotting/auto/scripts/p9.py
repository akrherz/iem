"""
This chart produces the daily climatology of
Degree Days for a location of your choice. Please note that
Feb 29 is not considered for this analysis.
"""
import datetime

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

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
    thisyear = datetime.date.today().year
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
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


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    thisyear = datetime.datetime.now().year
    year = ctx["year"]
    base = ctx["base"]
    ceiling = ctx["ceiling"]
    varname = ctx["var"]

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown Station Metadata.")
    syear = max(ab.year, 1893)

    glabel = f"{varname}{base}{ceiling}"
    gfunc = f"gddxx({base}, {ceiling}, high, low)"
    title = f"base={base}/ceil={ceiling}"
    if varname in ["hdd", "cdd"]:
        gfunc = f"{varname}(high, low, {base})"
        title = f"base={base}"
    elif varname == "sdd":
        gfunc = f"case when high > {ceiling} then high - {ceiling} else 0 end"
        title = f"base={ceiling}"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""SELECT year, sday, {gfunc} as {glabel} from alldata WHERE
            station = :sid and year > 1892 and sday != '0229'
            and sday >= :sday and sday <= :eday ORDER by day ASC
            """
            ),
            conn,
            params={
                "sid": station,
                "sday": f"{ctx['sday']:%m%d}",
                "eday": f"{ctx['eday']:%m%d}",
            },
        )
    if df.empty:
        raise NoDataFound("No data Found.")

    if ctx["w"] == "ytd":
        df["accum"] = df[["year", glabel]].groupby("year").cumsum()
        glabel = "accum"
    df2 = (
        df[["sday", glabel]]
        .groupby("sday")
        .describe(percentiles=[0.05, 0.25, 0.75, 0.95])
    )
    df2 = df2.unstack(level=-1)
    tt = f"{ctx['sday']:%-d %b} thru {ctx['eday']:%-d %b}"
    title = (
        f"({syear}-{thisyear}) [{tt}] {ctx['_sname']}\n"
        f"{year} {PDICT[varname]} ({title})"
    )
    # collapse the multi-index for columns
    retdf = df2.reset_index().pivot(index="sday", columns="level_1", values=0)
    # avoid leap year
    xaxis = pd.to_datetime(
        "2001" + retdf.reset_index()["sday"], format="%Y%m%d"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.plot(
        xaxis,
        df2[(glabel, "mean")],
        color="r",
        zorder=2,
        lw=2.0,
        label="Average",
    )
    _data = df[df["year"] == year][[glabel, "sday"]].sort_values(by="sday")
    ax.scatter(
        pd.to_datetime("2001" + _data["sday"], format="%Y%m%d"),
        _data[glabel],
        color="b",
        zorder=2,
        label=f"{year}",
    )
    ax.bar(
        xaxis,
        df2[(glabel, "95%")] - df2[(glabel, "5%")],
        bottom=df2[(glabel, "5%")],
        ec="tan",
        fc="tan",
        zorder=1,
        label="5-95 Percentile",
    )
    ax.bar(
        xaxis,
        df2[(glabel, "75%")] - df2[(glabel, "25%")],
        bottom=df2[(glabel, "25%")],
        ec="lightblue",
        fc="lightblue",
        zorder=1,
        label="25-75 Percentile",
    )
    ax.set_xlim(xaxis.values[0], xaxis.values[-1])
    if varname == "gdd" and ctx["w"] == "daily":
        ax.set_ylim(-0.25, 40)
    ax.grid(True)
    ax.set_ylabel(f"{PDICT2[ctx['w']]}" r" $^{\circ}\mathrm{F}$")
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-d %b"),
    )
    ax.legend(ncol=2)

    return fig, retdf


if __name__ == "__main__":
    plotter({})
