"""
This application generates a comparison of daily
high and low temperatures between two automated ASOS sites of your
choosing.
"""

from datetime import date, timedelta
from typing import Annotated

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot.description import (
    DateArg,
    PlotDescription,
    SelectArg,
    ZStationArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "temp": "High and Low Temperature",
    "dewp": "High and Low Dew Point Temp",
}


class Params(AutoplotParams):
    """Request parameters."""

    zstation1: Annotated[
        str, ZStationArg(network="IA_ASOS", label="Select Station 1:")
    ] = "DSM"
    zstation2: Annotated[
        str, ZStationArg(network="IA_ASOS", label="Select Station 2:")
    ] = "IKV"
    var: Annotated[
        str,
        SelectArg(
            options=PDICT, label="Select variable to plot comparison of"
        ),
    ] = "temp"
    sdate: Annotated[
        date,
        DateArg(
            label="Start Date:",
            default=lambda: (date.today() - timedelta(days=90)).strftime(
                "%Y/%m/%d"
            ),
        ),
    ]
    edate: Annotated[
        date,
        DateArg(
            label="End Date:",
            default=lambda: date.today().strftime("%Y/%m/%d"),
        ),
    ]


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=86400
    )


def plotter(ctx: Params):
    """Go"""
    station1 = ctx.zstation1
    station2 = ctx.zstation2
    sdate = ctx.sdate
    edate = ctx.edate
    varname = ctx.var

    d = "tmpf" if varname == "temp" else "dwpf"
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper(
                """
WITH one as (
    SELECT day, max_{d}, min_{d} from summary s JOIN stations t on
    (s.iemid = t.iemid) WHERE t.id = :station1 and t.network = :network1 and
    s.day >= :sdate and s.day <= :edate),

two as (
    SELECT day, max_{d}, min_{d} from summary s JOIN stations t on
    (s.iemid = t.iemid) WHERE t.id = :station2 and t.network = :network2 and
    s.day >= :sdate and s.day <= :edate)

        SELECT one.day as day,
        one.max_{d} as one_high, one.min_{d} as one_low,
        two.max_{d} as two_high, two.min_{d} as two_low
        from one JOIN two on (one.day = two.day) ORDER by day ASC
        """,
                d=d,
            ),
            conn,
            params={
                "station1": station1,
                "network1": ctx["network1"],
                "sdate": sdate,
                "edate": edate,
                "station2": station2,
                "network2": ctx["network2"],
            },
            index_col="day",
        )
    if df.empty:
        raise NoDataFound("No data found for this comparison")
    df["high_diff"] = df["one_high"] - df["two_high"]
    df["low_diff"] = df["one_low"] - df["two_low"]

    fig = figure(
        title=(
            f"[{station1}] {ctx['_nt1'].sts[station1]['name']} minus "
            f"[{station2}] {ctx['_nt2'].sts[station2]['name']}"
        ),
        subtitle=(
            f"{PDICT[varname]} Difference: "
            f"{sdate:%-d %b %Y} - {edate:%-d %b %Y}"
        ),
        apctx=ctx,
    )
    ax = fig.subplots(2, 1, sharex=True)

    for i, vname in enumerate(["high", "low"]):
        col = f"{vname}_diff"
        df2 = df[df[col] > 0]
        freq1 = len(df2.index) / float(len(df.index)) * 100.0
        ax[i].bar(df2.index.values, df2[col].values, fc="r", ec="r")
        df2 = df[df[col] < 0]
        freq2 = len(df2.index) / float(len(df.index)) * 100.0
        ax[i].bar(df2.index.values, df2[col].values, fc="b", ec="b")
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
        ax[i].grid(True)
        ax[i].text(
            0.5,
            0.95,
            f"{station1} Higher ({freq1:.1f}%)",
            transform=ax[i].transAxes,
            va="top",
            ha="center",
            bbox={"color": "w"},
            color="r",
            fontsize=8,
        )
        ax[i].text(
            0.5,
            0.01,
            f"{station2} Higher ({freq2:.1f}%)",
            transform=ax[i].transAxes,
            va="bottom",
            ha="center",
            bbox={"color": "w"},
            color="b",
            fontsize=8,
        )
        ax[i].text(
            0.95,
            0.99,
            f"Bias: {df[col].mean():.2f}",
            transform=ax[i].transAxes,
            va="top",
            ha="right",
            color="k",
            bbox={"color": "w"},
            fontsize=8,
        )
        ax[i].set_ylabel(
            f"{vname.capitalize()} {varname.capitalize()} Difference °F"
        )
        rng = df[col].max() - df[col].min()
        ax[i].set_ylim(df[col].min() - 0.2 * rng, df[col].max() + 0.2 * rng)

    return fig, df
