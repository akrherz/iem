"""
This application plots frequencies of a variable
of your choice for five bins of your choice.  These five bins represent
inclusive ranges and may overlap, if so desired.  The range entries below
are in units of inches or Fahrenheit where appropriate.  The date selection
sets the year-to-date period used for each year.

<p><strong>Updated 17 March 2021</strong>: The range parameters were
updated to be space delimited so to allow negative numbers to be used.
"""

import datetime as dt
from datetime import date
from typing import Annotated

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import (
    DateArg,
    PlotDescription,
    SelectArg,
    TextArg,
    YearArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "avgt": "Average Temperature",
    "high": "High Temperature",
    "low": "Low Temperature",
    "precip": "Precipitation",
    "snow": "Snowfall",
}


def parse_range(rng: str) -> list[float]:
    """Convert this into bins"""
    if rng.find(" ") == -1:
        raise NoDataFound("Invalid Range Provided")
    return [
        float(f) for f in rng.replace("to", "").replace("T", "0.0001").split()
    ]


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    date: Annotated[
        dt.date,
        DateArg(
            label="Select Year-to-Date End Date (inclusive):",
            default=lambda: date.today().strftime("%Y/%m/%d"),
        ),
    ]
    year: Annotated[
        int,
        YearArg(
            label="Additional Year to Compare:",
            default=lambda: date.today().year - 1,
        ),
    ]
    var: Annotated[
        str, SelectArg(options=PDICT, label="Variable to Plot:")
    ] = "high"
    r1: Annotated[
        str, TextArg(label="Range #1 (inclusive, space separated)")
    ] = "50 59"
    r2: Annotated[
        str, TextArg(label="Range #2 (inclusive, space separated)")
    ] = "60 69"
    r3: Annotated[
        str, TextArg(label="Range #3 (inclusive, space separated)")
    ] = "70 79"
    r4: Annotated[
        str, TextArg(label="Range #4 (inclusive, space separated)")
    ] = "80 89"
    r5: Annotated[
        str, TextArg(label="Range #5 (inclusive, space separated)")
    ] = "90 99"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    try:
        r1 = parse_range(ctx.r1)
        r2 = parse_range(ctx.r2)
        r3 = parse_range(ctx.r3)
        r4 = parse_range(ctx.r4)
        r5 = parse_range(ctx.r5)
    except ValueError as exp:
        raise NoDataFound("Invalid Range Provided") from exp
    dt = ctx.date
    year = ctx.year
    varname = ctx.var

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT year, day, high, low, precip, snow,
            (high + low) / 2. as avgt from alldata WHERE station = :station and
            extract(doy from day) <= extract(doy from :dt)
        """),
            conn,
            params={"station": station, "dt": dt},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    for i, rng in enumerate([r1, r2, r3, r4, r5]):
        if len(rng) != 2 or rng[0] > rng[1]:
            raise NoDataFound("Invalid Range Provided")
        df[f"cnt{i + 1}"] = 0
        df.loc[
            ((df[varname] >= rng[0]) & (df[varname] <= rng[1])),
            f"cnt{i + 1}",
        ] = 1

    gdf = (
        df[["cnt1", "cnt2", "cnt3", "cnt4", "cnt5", "year"]]
        .groupby("year")
        .sum()
    )

    title = f"{ctx.sname} :: Jan 1 - {dt:%b %-d} {PDICT[varname]} Days"
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    bars = ax.bar(
        np.arange(1, 6) - 0.25, gdf.mean().values, width=-0.25, label="Average"
    )
    for mybar in bars:
        ax.text(
            mybar.get_x() - 0.125,
            mybar.get_height() + 0.5,
            f"{mybar.get_height():.1f}",
            fontsize=14,
            ha="center",
        )

    if year in gdf.index:
        bars = ax.bar(
            range(1, 6), gdf.loc[year].values, width=0.25, label=str(year)
        )
        for mybar in bars:
            ax.text(
                mybar.get_x() + 0.125,
                mybar.get_height() + 0.5,
                f"{mybar.get_height():.0f}",
                fontsize=14,
                ha="center",
            )

    if dt.year in gdf.index:
        bars = ax.bar(
            np.arange(1, 6) + 0.25,
            gdf.loc[dt.year].values,
            width=0.25,
            label=str(dt.year),
        )
        for mybar in bars:
            ax.text(
                mybar.get_x() + 0.125,
                mybar.get_height() + 0.5,
                f"{mybar.get_height():.0f}",
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
