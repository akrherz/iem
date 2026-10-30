"""
This plot displays the frequency of having a
reported wind speed be above a given threshold by reported temperature
and by month.
"""

import calendar
from datetime import datetime
from typing import Annotated

import matplotlib.patheffects as PathEffects
import pandas as pd
from pyiem.database import get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot.description import (
    IntArg,
    MonthArg,
    PlotDescription,
    ZStationArg,
)
from iemweb.autoplot.params import AutoplotParams


class Params(AutoplotParams):
    """Request parameters."""

    zstation: Annotated[
        str, ZStationArg(network="IA_ASOS", label="Select Station:")
    ] = "DSM"
    threshold: Annotated[int, IntArg(label="Wind Speed Threshold (knots)")] = (
        10
    )
    month: Annotated[int, MonthArg(label="Select Month:")] = 3


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=86400
    )


def plotter(ctx: Params):
    """Go"""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    station = ctx.zstation
    threshold = ctx.threshold
    month = ctx.month

    cursor.execute(
        """
        WITH data as (
            SELECT tmpf::int as t, sknt from alldata where station = %s
            and extract(month from valid) = %s and tmpf is not null
            and sknt >= 0
        )

        SELECT t, sum(case when sknt >= %s then 1 else 0 end), count(*)
        from data GROUP by t ORDER by t ASC
    """,
        (station, month, threshold),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data was Found.")
    tmpf = []
    events = []
    total = []
    hits = 0
    cnt = 0
    for row in cursor:
        if row[2] < 3:
            continue
        tmpf.append(row[0])
        hits += row[1]
        cnt += row[2]
        events.append(row[1])
        total.append(row[2])

    df = pd.DataFrame(
        dict(
            tmpf=pd.Series(tmpf),
            events=pd.Series(events),
            total=pd.Series(total),
        )
    )

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = (
        f"{ctx.sname}\n"
        f"Frequency of {threshold}+ knot Wind Speeds by Temperature "
        f"for {calendar.month_name[month]} "
        f"({ab.year}-{datetime.now().year})\n"
        "(must have 3+ hourly observations at the given temperature)"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.bar(
        tmpf,
        df["events"] / df["total"] * 100.0,
        width=1.1,
        ec="green",
        fc="green",
    )
    avgval = hits / float(cnt) * 100.0
    ax.axhline(avgval, lw=2, zorder=2)
    txt = ax.text(
        tmpf[10],
        avgval + 1,
        f"Average: {avgval:.1f}%",
        va="bottom",
        zorder=2,
        color="yellow",
        fontsize=14,
    )
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])
    ax.grid(zorder=11)
    ax.set_ylabel("Frequency [%]")
    ax.set_ylim(0, 100)
    ax.set_xlim(min(tmpf) - 3, max(tmpf) + 3)
    ax.set_xlabel("Air Temperature °F")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])

    return fig, df
