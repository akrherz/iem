"""
This autoplot generates a probability of a specified accumulation threshold
being reached by the given calendar date.  This is based on period of record
observations, so it is an observed frequency.
"""

from datetime import date
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import (
    FloatArg,
    IntArg,
    PlotDescription,
    SDayArg,
    SelectArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "accum_gdd": "Growing Degree Days",
    "accum_precip": "Precipitation",
}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    sday: Annotated[
        date,
        SDayArg(label="Select start date to accumulate from:", default="0501"),
    ]
    var: Annotated[
        str, SelectArg(options=PDICT, label="Which variable to plot?")
    ] = "accum_gdd"
    gddbase: Annotated[
        int, IntArg(label="Growing Degree Day Base Temperature:")
    ] = 50
    gddceil: Annotated[
        int, IntArg(label="Growing Degree Day Ceiling Temperature:")
    ] = 86
    threshold: Annotated[
        float, FloatArg(label="Accumulation Threshold (F or inch):")
    ] = 1100


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def get_obsdf(ctx: Params):
    """Figure out our observations."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
                SELECT day, year,
                extract(doy from day) as day_of_year,
                sum(gddxx(:gddbase, :gddceil, high, low))
                    OVER (PARTITION by year ORDER by day ASC) as accum_gdd,
                sum(precip) OVER (PARTITION by year ORDER by day ASC)
                    as accum_precip from alldata
                WHERE station = :station and sday >= :sday ORDER by day ASC
            """
            ),
            conn,
            index_col="day",
            parse_dates=["day"],
            params={
                "station": ctx.station,
                "sday": ctx.sday.strftime("%m%d"),
                "gddbase": ctx.gddbase,
                "gddceil": ctx.gddceil,
            },
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    # Check the first year to see if it starts on our sday
    if df.index[0].strftime("%m%d") != ctx.sday.strftime("%m%d"):
        df = df[df["year"] > df.index[0].year]
    # compute the accumulated frequency of accumulated value by day of year
    # over the given threshold
    df["over_threshold"] = df[ctx.var] > ctx.threshold
    # if the last year is not over threshold, chomp it off too
    if not df.iloc[-1]["over_threshold"]:
        df = df[df["year"] < df.index.year.max()]
    return df


def plotter(ctx: Params):
    """Go"""
    df = get_obsdf(ctx)

    # Compute the climatology
    df2 = (
        df[["over_threshold", "day_of_year"]].groupby("day_of_year").mean()
        * 100.0
    )
    title = PDICT[ctx.var]
    if ctx.var == "accum_gdd":
        title += f" ({ctx.gddbase}/{ctx.gddceil})"

    units = "inch" if ctx.var == "accum_precip" else "GDD"
    fig = figure(
        title=(
            f"({df.index[0].year}-{df.index[-1].year}) {ctx.sname}:: {title}"
        ),
        subtitle=(
            f"Accumulation over {ctx.threshold} {units} "
            f"after {ctx.sday:%b %-d}"
        ),
        apctx=ctx,
    )
    ax = fig.add_axes((0.06, 0.1, 0.65, 0.78))
    ax.plot(df2.index.values, df2["over_threshold"].values, color="k")

    ax.set_ylim(0, 101)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylabel("Accumulated Frequency [%]")

    # Set xlim to something that covers the range of data
    df3 = df2[(df2["over_threshold"] > 0) & (df2["over_threshold"] < 100)]
    if df3.empty:
        raise NoDataFound("No values found over threshold.")
    ax.set_xlim(df3.index.min() - 5, df3.index.max() + 5)
    ax.grid(True)
    xticks = []
    xticklabels = []
    # careful
    mindoy = max(0, df3.index.min() - 5)
    maxdoy = min(365, df3.index.max() + 5)
    dt1 = pd.Timestamp("2000-01-01") + pd.Timedelta(days=mindoy)
    dt2 = pd.Timestamp("2000-01-01") + pd.Timedelta(days=maxdoy)
    every = [1, 8, 15, 22]
    if dt2.day_of_year - dt1.day_of_year > 60:
        every = [1, 15]
    if dt2.day_of_year - dt1.day_of_year > 120:
        every = [
            1,
        ]
    for dt in pd.date_range(dt1, dt2):
        if dt.day in every:
            xticks.append(dt.day_of_year)
            xticklabels.append(dt.strftime("%b %d"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    # Print a table of percentile values
    table = "Date    Percentile\n"
    thresh = 0
    for i, row in df2.iterrows():
        if row["over_threshold"] > thresh:
            dt = pd.Timestamp("2000-01-01") + pd.Timedelta(days=i)
            table += f"{dt:%b %d}  {thresh:02d}\n"
            thresh += 5 if thresh < 94 else 4
    fig.text(
        0.75,
        0.75,
        table,
        va="top",
        ha="left",
        family="monospace",
        fontsize=12,
    )

    return fig, df2
