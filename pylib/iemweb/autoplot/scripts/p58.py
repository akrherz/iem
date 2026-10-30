"""
Displays the number of times that a single day's
precipitation was greater than some portion of the monthly total. The
default settings provide the frequency of getting half of the month's
precipitation within one 24 hour period.
"""

import calendar
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import PlotDescription, TextArg
from iemweb.autoplot.params import AutoplotParams


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    threshold: Annotated[
        str, TextArg(label="Percentage of Monthly Precipitation on One Day")
    ] = "50"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    threshold = float(ctx.threshold)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
            WITH monthly as (
            SELECT year, month, max(precip), sum(precip)
            from alldata
            WHERE station = :station
                       and precip is not null GROUP by year, month)

            SELECT month,
            sum(case when max > (sum * :thres) then 1 else 0 end) as hits,
            max(case when max > (sum * :thres) then year else null end)
                as last_year,
            count(*) as years from monthly GROUP by month ORDER by month ASC
            """),
            conn,
            params={"station": station, "thres": threshold / 100.0},
            index_col="month",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["freq"] = df["hits"] / df["years"] * 100.0

    title = (
        f"{ctx.sname}\n"
        f"Frequency of one day having >= {threshold:.0f}% of that month's "
        "precip total"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)

    ax.bar(df.index, df["freq"], align="center")
    for i, row in df.iterrows():
        label = f"{row['freq']:.1f}%\n{row['last_year']:.0f}"
        if pd.isna(row["last_year"]):
            label = "None"
        ax.text(
            i,
            row["freq"] + 2,
            label,
            ha="center",
            bbox=dict(color="white"),
        )
    ax.grid(True)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0, 100 if df["freq"].max() < 90 else 115)
    ax.set_ylabel(f"Percentage of Years, out of {df['years'].max():.0f} total")
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlabel("Year of last occurrence shown")

    return fig, df
