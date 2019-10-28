"""Temperature/Precip/Snow Ranges"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("precip", "Precipitation"),
        ("avgt", "Average Temperature"),
        ("high", "High Temperature"),
        ("low", "Low Temperature"),
        ("precip", "Precipitation"),
        ("snow", "Snowfall"),
    ]
)


def parse_range(rng):
    """Convert this into bins"""
    return [float(f) for f in rng.split("-")]


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This application plots frequencies of a variable
    of your choice for five bins of your choice.  These five bins represent
    inclusive ranges and may overlap, if so desired.  The range entries below
    are in units of inches or Fahrenheit where appropriate.  The date selection
    sets the year-to-date period used for each year.
    """
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="Select Year-to-Date End Date (inclusive):",
        ),
        dict(
            type="year",
            name="year",
            default=(today.year - 1),
            label="Additional Year to Compare:",
        ),
        dict(
            type="select",
            name="var",
            options=PDICT,
            default="high",
            label="Variable to Plot:",
        ),
        dict(
            type="text",
            name="r1",
            default="50-59",
            label="Range #1 (inclusive)",
        ),
        dict(
            type="text",
            name="r2",
            default="60-69",
            label="Range #2 (inclusive)",
        ),
        dict(
            type="text",
            name="r3",
            default="70-79",
            label="Range #3 (inclusive)",
        ),
        dict(
            type="text",
            name="r4",
            default="80-89",
            label="Range #4 (inclusive)",
        ),
        dict(
            type="text",
            name="r5",
            default="90-99",
            label="Range #5 (inclusive)",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    r1 = parse_range(ctx["r1"])
    r2 = parse_range(ctx["r2"])
    r3 = parse_range(ctx["r3"])
    r4 = parse_range(ctx["r4"])
    r5 = parse_range(ctx["r5"])
    date = ctx["date"]
    year = ctx["year"]
    varname = ctx["var"]

    dbconn = get_dbconn("coop")

    table = "alldata_%s" % (station[:2],)
    df = read_sql(
        """
        SELECT year, day, high, low, precip, snow,
        (high + low) / 2. as avgt from """
        + table
        + """ WHERE
        station = %s and extract(doy from day) <= extract(doy from %s::date)
    """,
        dbconn,
        params=(station, date),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    for i, rng in enumerate([r1, r2, r3, r4, r5]):
        df["cnt%s" % (i + 1,)] = 0
        df.loc[
            ((df[varname] >= rng[0]) & (df[varname] <= rng[1])),
            "cnt%s" % (i + 1,),
        ] = 1

    gdf = (
        df[["cnt1", "cnt2", "cnt3", "cnt4", "cnt5", "year"]]
        .groupby("year")
        .sum()
    )

    (fig, ax) = plt.subplots(1, 1)
    bars = ax.bar(
        np.arange(1, 6) - 0.25, gdf.mean().values, width=-0.25, label="Average"
    )
    for i, mybar in enumerate(bars):
        ax.text(
            mybar.get_x() - 0.35,
            mybar.get_height() + 0.5,
            "%.1f" % (mybar.get_height(),),
        )

    bars = ax.bar(
        range(1, 6), gdf.loc[year].values, width=0.25, label=str(year)
    )
    for i, mybar in enumerate(bars):
        ax.text(
            mybar.get_x(),
            mybar.get_height() + 0.5,
            "%.0f" % (mybar.get_height(),),
        )

    bars = ax.bar(
        np.arange(1, 6) + 0.25,
        gdf.loc[date.year].values,
        width=0.25,
        label=str(date.year),
    )
    for i, mybar in enumerate(bars):
        ax.text(
            mybar.get_x(),
            mybar.get_height() + 0.5,
            "%.0f" % (mybar.get_height(),),
        )
    ax.grid(True)
    ax.set_xticks(range(1, 6))
    ax.set_xticklabels(
        ["%g - %g" % (one, two) for (one, two) in [r1, r2, r3, r4, r5]]
    )
    ax.legend(loc="best")
    ax.set_ylabel("Days")
    ax.set_xlabel("%s (Ranges Inclusive)" % (PDICT[varname],))
    ax.set_title(
        ("Jan 1 - %s %s Days\n" "[%s] %s")
        % (
            date.strftime("%b %-d"),
            PDICT[varname],
            station,
            ctx["_nt"].sts[station]["name"],
        )
    )

    return fig, gdf


if __name__ == "__main__":
    plotter(dict())
