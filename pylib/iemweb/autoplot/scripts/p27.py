"""
This chart presents the date of the first fall
(date after 1 July) temperature below threshold 1 and then the number of
days after that date until threshold 2 was reached. The slanted dashed
lines are used to translate the dots to the date of occurrence for the
second threshold.
"""

from datetime import datetime, timedelta
from typing import Annotated

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from scipy.stats import linregress

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import IntArg, PlotDescription
from iemweb.autoplot.params import AutoplotParams


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    t1: Annotated[int, IntArg(label="Temperature Threshold 1:")] = 32
    t2: Annotated[int, IntArg(label="Temperature Threshold 2:")] = 29


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    t1 = ctx.t1
    t2 = ctx.t2
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT year,
            min(low) as min_low,
            min(case when low < %s then extract(doy from day)
                else 999 end) as t1_doy,
            min(case when low < %s then extract(doy from day)
                else 999 end) as t2_doy
            from alldata where station = %s and month > 6
            GROUP by year ORDER by year ASC
        """,
            conn,
            params=(t1, t2, station),
            index_col="year",
        )
    if not df.empty:
        df = df[df["t2_doy"] < 400]
    if df.empty:
        raise NoDataFound("No data was found after applying filter.")

    doy = np.array(df["t1_doy"], "i")
    doy2 = np.array(df["t2_doy"], "i")

    sts = datetime(2000, 1, 1)
    xticks = []
    xticklabels = []
    for i in range(min(doy), max(doy2) + 1):
        ts = sts + timedelta(days=i)
        if ts.day in [1, 8, 15, 22]:
            xticks.append(i)
            fmt = "%b %-d" if ts.day == 1 else "%-d"
            xticklabels.append(ts.strftime(fmt))

    title = f"{ctx.sname}\nFirst Fall Temperature Occurences"
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.scatter(doy, doy2 - doy)

    for x in xticks:
        ax.plot((x - 100, x), (100, 0), ":", c="#000000")

    h_slope, intercept, r_value, _, _ = linregress(
        df["t1_doy"].values, df["t2_doy"].values - df["t1_doy"].values
    )
    x = np.array(ax.get_xlim())
    ax.plot(x, h_slope * x + intercept, lw=2, color="r")
    ax.text(
        0.95,
        0.91,
        f"slope: {h_slope:.2f} days/day, R$^2$={(r_value**2):.2f}",
        bbox=dict(color="white"),
        transform=ax.transAxes,
        va="bottom",
        ha="right",
        color="r",
    )

    ax.set_ylim(-1, max(doy2 - doy) + 4)
    ax.set_xlim(min(doy) - 4, max(doy) + 4)
    ax.set_ylabel(f"Days until first sub {t2}°F")
    ax.set_xlabel(f"First day of sub {t1}°F")

    ax.grid(True)

    return fig, df
