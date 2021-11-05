"""Temperature/Precip/Snow Ranges"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound

PDICT = dict(
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
    return [float(f) for f in rng.split()]


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This application plots frequencies of a variable
    of your choice for five bins of your choice.  These five bins represent
    inclusive ranges and may overlap, if so desired.  The range entries below
    are in units of inches or Fahrenheit where appropriate.  The date selection
    sets the year-to-date period used for each year.

    <p><strong>Updated 17 March 2021</strong>: The range parameters were
    updated to be space delimited so to allow negative numbers to be used.
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
            default="50 59",
            label="Range #1 (inclusive, space separated)",
        ),
        dict(
            type="text",
            name="r2",
            default="60 69",
            label="Range #2 (inclusive, space separated)",
        ),
        dict(
            type="text",
            name="r3",
            default="70 79",
            label="Range #3 (inclusive, space separated)",
        ),
        dict(
            type="text",
            name="r4",
            default="80 89",
            label="Range #4 (inclusive, space separated)",
        ),
        dict(
            type="text",
            name="r5",
            default="90 99",
            label="Range #5 (inclusive, space separated)",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
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

    df = read_sql(
        f"""
        SELECT year, day, high, low, precip, snow,
        (high + low) / 2. as avgt from alldata_{station[:2]} WHERE
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

    title = "[%s] %s :: Jan 1 - %s %s Days" % (
        station,
        ctx["_nt"].sts[station]["name"],
        date.strftime("%b %-d"),
        PDICT[varname],
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    bars = ax.bar(
        np.arange(1, 6) - 0.25, gdf.mean().values, width=-0.25, label="Average"
    )
    for i, mybar in enumerate(bars):
        ax.text(
            mybar.get_x() - 0.125,
            mybar.get_height() + 0.5,
            "%.1f" % (mybar.get_height(),),
            fontsize=14,
            ha="center",
        )

    bars = ax.bar(
        range(1, 6), gdf.loc[year].values, width=0.25, label=str(year)
    )
    for i, mybar in enumerate(bars):
        ax.text(
            mybar.get_x() + 0.125,
            mybar.get_height() + 0.5,
            "%.0f" % (mybar.get_height(),),
            fontsize=14,
            ha="center",
        )

    bars = ax.bar(
        np.arange(1, 6) + 0.25,
        gdf.loc[date.year].values,
        width=0.25,
        label=str(date.year),
    )
    for i, mybar in enumerate(bars):
        ax.text(
            mybar.get_x() + 0.125,
            mybar.get_height() + 0.5,
            "%.0f" % (mybar.get_height(),),
            fontsize=14,
            ha="center",
        )
    ax.grid(True)
    ax.set_xticks(range(1, 6))
    ax.set_xticklabels(
        ["%g thru %g" % (one, two) for (one, two) in [r1, r2, r3, r4, r5]]
    )
    ax.legend(loc="best")
    ax.set_ylabel("Days")
    ax.set_ylim(top=ax.get_ylim()[1] + 1)
    ax.set_xlabel(f"{PDICT[varname]} (Ranges Inclusive)")

    return fig, gdf


if __name__ == "__main__":
    plotter(dict())
