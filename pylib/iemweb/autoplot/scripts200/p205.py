"""
The IEM computes daily summaries of ASOS station
data based on available station summaries and computed summaries based
on available hourly data.  This chart presents the frequency combination
of one or more variables.  Please let us know if you want additional
fields added to this tool.
"""

import calendar
import itertools
from typing import TYPE_CHECKING, Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot.description import (
    IntArg,
    PlotDescription,
    TextArg,
    ZStationArg,
)
from iemweb.autoplot.params import AutoplotParams

if TYPE_CHECKING:
    from datetime import datetime


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[
        str, ZStationArg(label="Select Station", network="IA_ASOS")
    ] = "DSM"
    max_tmpf_above: Annotated[
        int | None,
        IntArg(
            ge=-100,
            le=150,
            label="Daily Max Temperature Above (threshold F): [optional]",
            default=90,
        ),
    ] = None
    max_tmpf_range: Annotated[
        str | None,
        TextArg(
            label="Daily Max Temperature Inclusive Range (deg F): [optional]",
            default="70 to 79",
        ),
    ] = None
    min_tmpf_below: Annotated[
        int | None,
        IntArg(
            ge=-100,
            le=150,
            label="Daily Min Temperature Below (threshold F): [optional]",
            default=70,
        ),
    ] = None
    max_feel_above: Annotated[
        int | None,
        IntArg(
            ge=-100,
            le=150,
            label="Daily Max Feels Like Temp Above (threshold F): [optional]",
            default=90,
        ),
    ] = None
    min_feel_below: Annotated[
        int | None,
        IntArg(
            ge=-100,
            le=150,
            label="Daily Min Feels Like Temp Below (threshold F): [optional]",
            default=0,
        ),
    ] = None
    max_dwpf_below: Annotated[
        int | None,
        IntArg(
            ge=-70,
            le=100,
            label="Daily Maximum Dewpoint Below (threshold F): [optional]",
            default=50,
        ),
    ] = None
    max_dwpf_above: Annotated[
        int | None,
        IntArg(
            ge=-70,
            le=100,
            label="Daily Maximum Dewpoint Above (threshold F): [optional]",
            default=70,
        ),
    ] = None
    max_rh_below: Annotated[
        int | None,
        IntArg(
            ge=0,
            le=100,
            label="Daily Maximum Relative Humidity Below (%): [optional]",
            default=50,
        ),
    ] = None
    avg_smph_below: Annotated[
        int | None,
        IntArg(
            ge=0,
            le=150,
            label="Daily Average Wind Speed Below (threshold MPH): [optional]",
            default=10,
        ),
    ] = None
    max_smph_above: Annotated[
        int | None,
        IntArg(
            ge=0,
            le=150,
            label="Daily Max Wind Speed Above (threshold MPH): [optional]",
            default=50,
        ),
    ] = None
    max_smph_below: Annotated[
        int | None,
        IntArg(
            ge=0,
            le=150,
            label="Daily Max Wind Speed Below (threshold MPH): [optional]",
            default=50,
        ),
    ] = None
    max_gust_above: Annotated[
        int | None,
        IntArg(
            ge=0,
            le=150,
            label="Daily Max Wind Gust Above (threshold MPH): [optional]",
            default=50,
        ),
    ] = None
    max_gust_below: Annotated[
        int | None,
        IntArg(
            ge=0,
            le=150,
            label="Daily Max Wind Gust Below (threshold MPH): [optional]",
            default=50,
        ),
    ] = None


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    params = []
    labels = {"all_hit": "All Combined"}
    for ez in (
        "max_rh_below max_feel_above min_feel_below max_dwpf_below "
        "max_tmpf_above max_dwpf_above min_tmpf_below"
    ).split():
        val = ctx.get(ez)
        if val is None:
            continue
        col, op = ez.rsplit("_", 1)
        units = "%" if col.endswith("rh") else "F"
        op = ">=" if op == "above" else "<"
        params.append(
            f"case when {col} {op} {val:.0f} then 1 else 0 end as {ez}_hit"
        )
        labels[f"{ez}_hit"] = f"{col} {op} {val:.0f} {units}"
    if ctx.max_tmpf_range:
        tokens = [
            int(i) for i in ctx.max_tmpf_range.replace("+", " ").split("to")
        ]
        params.append(
            f"case when max_tmpf::int >= {tokens[0]} and "
            f"max_tmpf::int <= {tokens[1]} then 1 else 0 end as tmpf_hit"
        )
        labels["tmpf_hit"] = f"High Temp {tokens[0]:.0f}F - {tokens[1]:.0f}F"
    if ctx.avg_smph_below is not None:
        params.append(
            f"case when avg_sknt * 1.15 < {ctx.avg_smph_below:.0f} "
            "then 1 else 0 end as smph_hit"
        )
        labels["smph_hit"] = f"Avg Wind < {ctx.avg_smph_below:.0f}MPH"
    if ctx.max_gust_above is not None:
        params.append(
            f"case when max_gust * 1.15 > {ctx.max_gust_above:.0f} "
            "then 1 else 0 end as gust_hit"
        )
        labels["gust_hit"] = f"Wind Gust > {ctx.max_gust_above:.0f}MPH"
    elif ctx.max_gust_below is not None:
        params.append(
            f"case when max_gust * 1.15 < {ctx.max_gust_below:.0f} "
            "then 1 else 0 end as gust_hit"
        )
        labels["gust_hit"] = f"Wind Gust < {ctx.max_gust_below:.0f}MPH"
    if ctx.max_smph_above is not None:
        params.append(
            f"case when max_sknt * 1.15 > {ctx.max_smph_above:.0f} "
            "then 1 else 0 end as max_smph_hit"
        )
        labels["max_smph_hit"] = (
            f"Max Wind Speed > {ctx.max_smph_above:.0f}MPH"
        )
    elif ctx.max_smph_below:
        params.append(
            f"case when max_sknt * 1.15 < {ctx.max_smph_below:.0f} "
            "then 1 else 0 end as max_smph_hit"
        )
        labels["max_smph_hit"] = (
            f"Max Wind Speed < {ctx.max_smph_below:.0f}MPH"
        )
    if not params:
        raise NoDataFound("Please select some options for plotting.")
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper(
                """
    SELECT {cols}, extract(doy from day) as doy,
    extract(month from day)::int as month from summary s JOIN stations t
    ON (s.iemid = t.iemid) WHERE t.id = :station and t.network = :network""",
                cols=" , ".join(params),
            ),
            conn,
            params={"station": station, "network": ctx["network"]},
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["all_hit"] = 1
    for col in df.columns:
        if col in ["doy", "month"]:
            continue
        df.loc[df[col] < 1, "all_hit"] = 0
    gdf = df.groupby("doy").mean()

    ab: datetime | None = ctx["_nt"].sts[station]["archive_begin"]
    title = (
        f"{ctx.sname} ({'n/a' if ab is None else ab.year}-) "
        "Daily Observed Frequency"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    colors = itertools.cycle(["r", "g", "b", "c", "m", "y"])
    for col in df.columns:
        if col in ["doy", "month"]:
            continue
        try:
            color = "k" if col == "all_hit" else next(colors)
        except StopIteration:
            color = "k"
        ax.plot(
            gdf.index.to_numpy(),
            gdf[col].to_numpy() * 100.0,
            lw=2,
            label=labels[col],
            color=color,
        )

    ax.legend(ncol=3, loc=(-0.05, -0.21), fontsize=14)
    starts = (1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
    # Grid lines at month starts, labels centered mid-month
    ax.set_xticks(starts)
    ax.set_xticklabels([])
    ax.set_xticks([s + 15 for s in starts], minor=True)
    ax.tick_params(axis="x", which="minor", length=0)

    monthly = df[["month", "all_hit"]].groupby("month").mean()
    xticklabels = []
    for month, row in monthly.iterrows():
        abbr = calendar.month_abbr[int(str(month))]
        xticklabels.append(
            f"{abbr}\n{row['all_hit'] * 100:.1f}%",
        )
    ax.set_xticklabels(xticklabels, minor=True)

    ax.set_position((0.1, 0.2, 0.75, 0.7))
    ax.set_xlim(1, 365)
    ax.set_ylim(-2, 102)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.set_ylabel("Daily Frequency [%]")
    ax2 = ax.twinx()
    ax2.set_ylabel("Daily Frequency [%]")
    ax2.set_ylim(-2, 102)
    ax2.set_position((0.1, 0.2, 0.75, 0.7))
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    return fig, gdf
