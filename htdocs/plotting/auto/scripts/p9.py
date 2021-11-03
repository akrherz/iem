"""GDD climo"""
import calendar
import datetime

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem import network
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "cdd": "Cooling Degree Days",
    "gdd": "Growing Degree Days",
    "hdd": "Heating Degree Days",
    "sdd": "Stress Degree Days",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart produces the daily climatology of
    Degree Days for a location of your choice. Please note that
    Feb 29 is not considered for this analysis."""
    thisyear = datetime.date.today().year
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
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
        dict(
            type="select",
            options=PDICT,
            default="gdd",
            name="var",
            label="Which variable to plot:",
        ),
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
    pgconn = get_dbconn("coop", user="nobody")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    thisyear = datetime.datetime.now().year
    year = ctx["year"]
    base = ctx["base"]
    ceiling = ctx["ceiling"]
    varname = ctx["var"]

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    ab = nt.sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown Station Metadata.")
    syear = max(ab.year, 1893)

    glabel = "%s%s%s" % (varname, base, ceiling)
    gfunc = "gddxx(%s, %s, high, low)" % (base, ceiling)
    title = "base=%s/ceil=%s" % (base, ceiling)
    if varname in ["hdd", "cdd"]:
        gfunc = "%s(high, low, %s)" % (varname, base)
        title = "base=%s" % (base,)
    elif varname == "sdd":
        gfunc = "case when high > %s then high - %s else 0 end" % (
            ceiling,
            ceiling,
        )
        title = "base=%s" % (ceiling,)

    df = read_sql(
        f"SELECT year, sday, {gfunc} as {glabel} from {table} WHERE "
        "station = %s and year > 1892 and sday != '0229'",
        pgconn,
        params=(station,),
    )
    if df.empty:
        raise NoDataFound("No data Found.")

    # Do some magic!
    df2 = (
        df[["sday", glabel]]
        .groupby("sday")
        .describe(percentiles=[0.05, 0.25, 0.75, 0.95])
    )
    df2 = df2.unstack(level=-1)
    title = "%s-%s %s [%s]\n%s %s (%s)" % (
        syear,
        thisyear,
        nt.sts[station]["name"],
        station,
        year,
        PDICT[varname],
        title,
    )
    (fig, ax) = figure_axes(title=title)
    ax.plot(
        np.arange(1, 366),
        df2[(glabel, "mean")],
        color="r",
        zorder=2,
        lw=2.0,
        label="Average",
    )
    _data = df[df["year"] == year][[glabel, "sday"]]
    _data.sort_values(by="sday", inplace=True)
    ax.scatter(
        np.arange(1, _data[glabel].shape[0] + 1),
        _data[glabel],
        color="b",
        zorder=2,
        label="%s" % (year,),
    )
    ax.bar(
        np.arange(1, 366),
        df2[(glabel, "95%")] - df2[(glabel, "5%")],
        bottom=df2[(glabel, "5%")],
        ec="tan",
        fc="tan",
        zorder=1,
        label="5-95 Percentile",
    )
    ax.bar(
        np.arange(1, 366),
        df2[(glabel, "75%")] - df2[(glabel, "25%")],
        bottom=df2[(glabel, "25%")],
        ec="lightblue",
        fc="lightblue",
        zorder=1,
        label="25-75 Percentile",
    )
    ax.set_xlim(0, 367)
    if varname == "gdd":
        ax.set_ylim(-0.25, 40)
    ax.grid(True)
    ax.set_ylabel(r"Daily Accumulation $^{\circ}\mathrm{F}$")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend(ncol=2)

    # collapse the multi-index for columns
    df = pd.DataFrame(df2)
    return fig, df


if __name__ == "__main__":
    plotter({})
