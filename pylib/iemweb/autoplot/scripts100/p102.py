"""
The National Weather Service issues Local Storm
Reports (LSRs) with a label associated with each report indicating the
source of the report.  This plot summarizes the number of reports
received each year by each source type.  The values are the ranks for
that year with 1 indicating the largest.  The values following the LSR
event type in parenthesis are the raw LSR counts for that year. You need
to graph at least two years worth of data to make this plot type work.
"""

from datetime import date
from typing import Annotated

import numpy as np
import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.reference import lsr_events

from iemweb.autoplot.description import (
    NetworkSelectArg,
    PlotDescription,
    SelectArg,
    YearArg,
)
from iemweb.autoplot.params import AutoplotParams

MARKERS = ["8", ">", "<", "v", "o", "h", "*"]


def _ltype_options() -> dict[str, str]:
    """LSR event types, sorted."""
    return {k: k for k in sorted(lsr_events)}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[
        str,
        NetworkSelectArg(network="WFO", all=True, label="Select WFO:"),
    ] = "DMX"
    ltype: Annotated[
        list[str] | None,
        SelectArg(
            multiple=True,
            options=_ltype_options(),
            default="TORNADO",
            label="Select LSR Event Types: (optional)",
        ),
    ] = None
    year: Annotated[int, YearArg(min=2006, label="Start Year")] = 2006
    eyear: Annotated[int, YearArg(min=2006, label="End Year (inclusive)")] = (
        Field(default_factory=lambda: date.today().year)
    )


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=3600
    )


def plotter(ctx: Params):
    """Go"""
    ctx["_nt"].sts["_ALL"] = dict(name="All WFOs")
    station = ctx.station[:4]
    syear = ctx.year
    eyear = ctx.eyear
    if syear == eyear:
        syear = eyear - 1
    ltype = ctx.ltype
    params = {"wfo": station if len(station) == 3 else station[1:]}
    wfo_limiter = " and wfo = :wfo "
    if station == "_ALL":
        wfo_limiter = ""
    typetext_limiter = ""
    if ltype:
        if len(ltype) == 1:
            typetext_limiter = " and typetext = :tt "
            params["tt"] = ltype[0]
        else:
            typetext_limiter = " and typetext = ANY(:tt)"
            params["tt"] = ltype
    params["sts"] = date(syear, 1, 1)
    params["ets"] = date(eyear + 1, 1, 1)
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            select extract(year from valid)::int as yr, upper(source) as src,
            count(*) from lsrs
            where valid > :sts and
            valid < :ets {wfo_limiter} {typetext_limiter}
            GROUP by yr, src
        """,
                wfo_limiter=wfo_limiter,
                typetext_limiter=typetext_limiter,
            ),
            conn,
            params=params,
        )
    if df.empty:
        raise NoDataFound("No data found")
    # pivot the table so that we can fill out zeros
    df = df.pivot(index="yr", columns="src", values="count")
    df = df.fillna(0).reset_index()
    df = df.melt(id_vars="yr", value_name="count")
    df["rank"] = df.groupby(["yr"])["count"].rank(
        ascending=False, method="first"
    )
    title = (
        f"NWS {ctx['_nt'].sts[station]['name']} "
        "Local Storm Report Sources Ranks"
    )
    if ltype:
        label = f"For LSR Types: {ltype}"
        if len(label) > 90:
            label = f"{label[:90]}..."
        title += f"\n{label}"
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    # Do syear as left side
    for year in range(syear, eyear):
        dyear = df[df["yr"] == year].sort_values(by=["rank"], ascending=True)
        if not dyear.empty:
            break
    i = 1
    ylabels = []
    leftsrcs = []
    usedline = 0
    for _, row in dyear.iterrows():
        src = row["src"]
        leftsrcs.append(src)
        ylabels.append(f"{src} ({row['count']:.0f})")
        d = df[df["src"] == src].sort_values(by=["yr"])
        ax.plot(
            np.array(d["yr"]),
            np.array(d["rank"]),
            lw=2,
            label=src,
            marker=MARKERS[usedline % len(MARKERS)],
        )
        i += 1
        usedline += 1
        if i > 20:
            break
    ax.set_yticks(range(1, len(ylabels) + 1))
    ax.set_yticklabels([f"{s} {i + 1}" for i, s in enumerate(ylabels)])
    ax.set_ylim(0.5, 20.5)

    ax2 = ax.twinx()
    # Do last year as right side
    dyear = df[df["yr"] == eyear].sort_values(by=["rank"], ascending=True)
    i = 0
    y2labels = []
    for _, row in dyear.iterrows():
        i += 1
        if i > 20:
            break
        src = row["src"]
        y2labels.append(f"{src} ({row['count']:.0f})")
        if src not in leftsrcs:
            d = df[df["src"] == src].sort_values(by=["yr"])
            ax.plot(
                np.array(d["yr"]),
                np.array(d["rank"]),
                lw=2,
                label=src,
                marker=MARKERS[usedline % len(MARKERS)],
            )
            usedline += 1

    ax2.set_yticks(range(1, len(y2labels) + 1))
    ax2.set_yticklabels([f"{i + 1} {s}" for i, s in enumerate(y2labels)])
    ax2.set_ylim(0.5, 20.5)

    pos = [0.2, 0.13, 0.6, 0.75]
    ax.set_position(pos)
    ax2.set_position(pos)
    ax.set_xticks(range(df["yr"].min(), df["yr"].max(), 2))
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    ax.grid()

    fig.text(0.15, 0.88, f"{syear}", fontsize=14, ha="center")
    fig.text(0.85, 0.88, f"{eyear}", fontsize=14, ha="center")

    return fig, df
