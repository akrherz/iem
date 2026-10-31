"""
This autoplot presents some metrics when comparing a single variable between
two airport weather stations.  The time zone of the first station is used for
the various subplots.  The top left panel shows a time series difference over
the period you selected.  The lower left panel shows a yearly mean value and
a +/- one standard deviation.
The top right panel shows a heatmap of the frequency of
the first station having a value greater than the second station by a certain
threshold.  The bottom right panel shows a violin plot of the monthly
distribution of differences.
"""

import calendar
from datetime import UTC, date, datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import utc

from iemweb.autoplot.description import (
    CmapArg,
    DateTimeArg,
    FloatArg,
    PlotDescription,
    SelectArg,
    ZStationArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "tmpf": "Air Temperature (°F)",
    "dwpf": "Dew Point (°F)",
    "sknt": "Wind Speed (knots)",
    "drct": "Wind Direction (degrees)",
    "alti": "Pressure Altimeter (inches)",
    "vsby": "Visibility (miles)",
    "gust": "Wind Gust (knots)",
    "feel": "Feels Like Temp (°F)",
    "mslp": "Mean Sea Level Pressure (mb)",
}


class Params(AutoplotParams):
    """Request parameters."""

    zstation1: Annotated[
        str, ZStationArg(network="IA_ASOS", label="Select Station 1:")
    ] = "AMW"
    zstation2: Annotated[
        str, ZStationArg(network="IA_ASOS", label="Select Station 2:")
    ] = "DSM"
    varname: Annotated[
        str, SelectArg(options=PDICT, label="Variable for Comparison")
    ] = "tmpf"
    sts: Annotated[
        datetime,
        DateTimeArg(
            label="Start Time (UTC):",
            min="1900/01/01 0000",
            default=lambda: utc().strftime("%Y/%m/%d 0000"),
        ),
    ]
    ets: Annotated[
        datetime,
        DateTimeArg(
            label="End Time (UTC):",
            min="1900/01/01 0000",
            max=lambda: utc().strftime("%Y/%m/%d 2359"),
            default=lambda: utc().strftime("%Y/%m/%d 2300"),
        ),
    ]
    cmap: Annotated[str, CmapArg(label="Color Map")] = "Greens"
    diff: Annotated[
        float, FloatArg(label="Difference Threshold for frequency heatmap")
    ] = 0


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=86400
    )


def plotter(ctx: Params):
    """Go"""
    sts = ctx.sts.replace(tzinfo=UTC)
    ets = ctx.ets.replace(tzinfo=UTC)
    station1 = ctx.zstation1
    station2 = ctx.zstation2
    varname = ctx.varname

    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        SELECT date_trunc('hour', valid + '10 minutes'::interval)
            at time zone 'UTC' as utc_valid,
        station, {varname} from alldata
        WHERE station = ANY(:stids) and {varname} is not null
        and report_type = 3
        order by utc_valid asc
        """,
                varname=varname,
            ),
            conn,
            params={"stids": [station1, station2]},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No data found with initial query.")
    df["utc_valid"] = df["utc_valid"].dt.tz_localize(UTC)
    tz = ZoneInfo(ctx["_nt1"].sts[station1]["tzname"] or "America/Chicago")
    df["local_valid"] = df["utc_valid"].dt.tz_convert(tz)
    df = df.pivot_table(
        index="local_valid", columns="station", values=varname, aggfunc="mean"
    )
    # drop any rows with NaN in either column
    df = df.dropna()
    if df.empty or station1 not in df.columns or station2 not in df.columns:
        raise NoDataFound("No data found after pivoting")
    df["diff"] = df[station1] - df[station2]

    fig = figure(
        title=(
            f"[{station1}] {ctx['_nt1'].sts[station1]['name']} minus "
            f"[{station2}] {ctx['_nt2'].sts[station2]['name']}"
        ),
        subtitle=(
            f"Hourly {PDICT[varname]} Difference "
            f"({sts.strftime('%-d %b %Y')} - {ets.strftime('%-d %b %Y')}) "
            f"POR: {df.index[0].strftime('%-d %b %Y')} - "
            f"{df.index[-1].strftime('%-d %b %Y')}"
        ),
        apctx=ctx,
    )
    # Plot the specified data period
    ax = fig.add_axes((0.08, 0.55, 0.5, 0.35))
    df2 = df.loc[sts:ets]
    if not df2.empty:
        ax.plot(df2.index, df2["diff"], label="Difference", lw=2)
        ax.set_ylabel(f"{PDICT[varname]} Difference")
        ax.grid(True)
        if ets - sts < timedelta(days=2):
            fmt = "%-I %p\n%-d %b"
        else:
            fmt = "%-d %b\n%Y"
        ax.xaxis.set_major_formatter(DateFormatter(fmt, tz=tz))

    # Plot the yearly means and standard deviation
    ax = fig.add_axes((0.08, 0.1, 0.5, 0.35))
    yearly = df["diff"].groupby(df.index.year).agg(["mean", "std"])
    ax.fill_between(
        yearly.index.values,
        yearly["mean"] - yearly["std"],
        yearly["mean"] + yearly["std"],
        color="lightgrey",
        label="+/- 1 \u03c3",
    )
    ax.plot(yearly.index.values, yearly["mean"], label="Mean", lw=2)
    ax.set_ylabel(f"{PDICT[varname]} Difference")
    ax.set_xlabel("Year")
    ax.grid(True)
    ax.legend(loc="best", ncol=2)

    # Plot the monthly distribution of differences as half violin plot
    ax = fig.add_axes((0.65, 0.1, 0.32, 0.3))
    monthly = df["diff"].groupby(df.index.month).apply(np.array)
    ax.violinplot(
        monthly.values, showextrema=False, showmeans=True, widths=0.7
    )
    ax.set_ylabel(f"{PDICT[varname]} Difference")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_title("Monthly Distribution")
    ax.grid(True)
    ptiles = df["diff"].quantile([0.01, 0.99])
    ax.set_ylim(ptiles.iloc[0], ptiles.iloc[1])

    # Plot the frequency of differences by week of year and hour of day
    df["hour"] = df.index.hour
    df["week"] = df.index.day_of_year // 7
    df["hit"] = np.where(df["diff"] >= ctx.diff, 1, 0)
    freq = df[["week", "hour", "hit"]].groupby(["week", "hour"]).mean()
    freq = freq.unstack(level="hour")
    H = freq.values
    ax = fig.add_axes((0.65, 0.53, 0.32, 0.32))
    res = ax.imshow(
        H * 100.0,
        aspect="auto",
        interpolation="nearest",
        extent=[0, 53, 0, 23],
        cmap=ctx.cmap,
    )
    fig.colorbar(res, ax=ax, label="Frequency [%]")
    units = PDICT[varname].split()[-1]
    ax.set_title(f"Freq {station1}-{station2} > {ctx.diff:.2f}{units}")
    ax.set_ylabel(ctx["_nt1"].sts[station1]["tzname"])
    ax.set_xlabel("Week of Year")
    ax.set_xticks(range(0, 53, 5))
    ax.set_yticks(range(0, 24, 3))
    ax.set_yticklabels(
        ["Mid", "3 AM", "6 AM", "9 AM", "Noon", "3 PM", "6 PM", "9 PM"]
    )
    # Label the x-axis with an approximate month
    ax.set_xticklabels(
        [
            (date(2000, 1, 1) + timedelta(days=int(x * 7))).strftime("%-d\n%b")
            for x in ax.get_xticks()
        ]
    )
    ax.grid(True)

    return fig, df
