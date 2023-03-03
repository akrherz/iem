"""
This produces an infographic with some of the information found
presented in NWS CLI reports.

<p>The high and low temperature gauges contain some extra statistical
information based on the period of record observations for the site. Sometimes
this period of record information comes from a nearby weather station. This
informatiom also provides the coldest high temperature and warmest low
temperature, both of which are not found within the raw CLI text product.
"""
# Local
from dataclasses import dataclass
from datetime import date, timedelta
from math import pi

# third party
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.reference import TRACE_VALUE
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, logger
from pyiem.exceptions import NoDataFound

LOG = logger()
TFORMAT = "%b %-d %Y %-I:%M %p %Z"


@dataclass
class GaugeParams:
    """Simple."""

    minval: float = None
    maxval: float = None
    avgval: float = None
    stddev: float = None
    ptiles: list = None


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 300}
    desc["defaults"] = {"_r": "t"}
    yest = date.today() - timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            default="KDSM",
            label="Select Station:",
            network="NWSCLI",
        ),
        dict(
            type="date",
            name="date",
            default=yest.strftime("%Y/%m/%d"),
            label="Select Date",
            min="2000/01/01",
        ),
    ]
    return desc


def miss(val):
    """Pretty."""
    if pd.isna(val):
        return "Missing"
    if np.allclose(val, TRACE_VALUE, 0.00001):
        return "Trace"
    return val


def gauge(ax, row, col, params):
    """Make the gauge plot."""
    if col == "high":
        if pd.notna(row["high_record"]):
            params.maxval = row["high_record"]
        if pd.notna(row["high_normal"]):
            params.avgval = row["high_normal"]
    else:
        if pd.notna(row["low_record"]):
            params.minval = float(row["low_record"])
        if pd.notna(row["low_normal"]):
            params.avgval = row["low_normal"]

    # Polar coordinates, so 0 is maxval and pi is minval
    colors = ["#BE0000", "#E48900", "#B6EB7A", "#0F4CBB", "#1B262C"]
    # Okay, the chart will go from maxval (rad=pi) to maxval (rad=0)
    bar_ends = [
        float(params.avgval + 2 * params.stddev),
        float(params.avgval + params.stddev),
        float(params.avgval - params.stddev),
        float(params.avgval - 2 * params.stddev),
        params.minval,
    ]
    labels = [r"2$\sigma$", r"$\sigma$", r"-$\sigma$", r"-2$\sigma$", ""]
    pos = 0
    positive_delta = float(params.maxval - params.avgval)
    negative_delta = float(params.avgval - params.minval)
    for val, color, label in zip(bar_ends, colors, labels):
        if val > params.avgval:
            ha = "left"
            if val > params.maxval:
                continue
            pos2 = (params.maxval - val) / positive_delta * pi / 2.0
        else:
            ha = "right"
            if val < params.minval:
                continue
            pos2 = pi / 2.0 + (
                (params.avgval - val) / negative_delta * pi / 2.0
            )
        ax.add_patch(Rectangle((pos, 1), pos2 - pos, 2, color=color))
        if abs(val - params.minval) > 1 and abs(val - params.maxval) > 1:
            ax.text(pos2, 3.1, f"{val:.0f}", ha=ha)
        ax.text(
            pos2,
            0.8,
            label,
            va="center",
            ha="left" if ha == "right" else "right",
        )
        pos = pos2
    # manual placement of max/min
    ax.text(
        0 if col == "low" else pi,
        3.1,
        f"{params.maxval:.0f}" if col == "low" else f"{params.minval:.0f}",
        ha="left" if col == "low" else "right",
    )

    # Add ticks for percentiles 10 through 90
    for val in params.ptiles:
        if val > params.avgval:
            pos = (params.maxval - val) / positive_delta * pi / 2.0
        else:
            pos = pi / 2.0 + (
                (params.avgval - val) / negative_delta * pi / 2.0
            )
        ax.add_patch(Rectangle((pos, 1), 0.001, 2, color="white"))

    # Tick for params.avgval
    ax.add_patch(Rectangle((pi / 2.0, 1), 0.001, 2, color="k"))
    # Median
    val = params.ptiles[4]
    if val > params.avgval:
        pos = (params.maxval - val) / positive_delta * pi / 2.0
    else:
        pos = pi / 2.0 + ((params.avgval - val) / negative_delta * pi / 2.0)
    ax.add_patch(Rectangle((pos, 1), 0.001, 2, color="r"))

    ax.grid(False)
    ax.set_xlim(0, pi)
    ax.set_xticks([])
    if row[col] >= params.avgval:
        theta = (params.maxval - row[col]) / positive_delta * (pi / 2.0)
        theta = max([0, theta])
    else:
        theta = (pi / 2.0) + (params.avgval - row[col]) / negative_delta * (
            pi / 2.0
        )
        theta = min([pi, theta])
    ax.text(
        -0.05 if col == "high" else pi + 0.05,
        2,
        f"Record: "
        rf"{miss(row[col + '_record'])}$^\circ$F"
        f"\n{', '.join([str(s) for s in row[col + '_record_years']])}",
        va="top",
        ha="left" if col == "high" else "right",
    )
    ax.text(
        pi / 2,
        3.25,
        "Avg:\n" + f"{miss(row[f'{col}_normal'])}" + r"$^\circ$F",
        ha="center",
    )
    ax.set_rorigin(-4.5)
    ax.set_yticks([])
    ax.arrow(
        theta,
        -4.5,
        0,
        5.5,
        width=0.1,
        head_width=0.2,
        head_length=1,
        fc="yellow",
        ec="k",
        clip_on=False,
    )
    ax.text(
        theta,
        -4.5,
        rf"{row[col]}$^\circ$F" f"\n@{row[col + '_time']} LST",
        ha="center",
        va="top",
        fontsize=14,
    )


def precip(fig, row, col):
    """Do the precip part."""
    ax = fig.add_axes([0.47, 0.57 if col == "precip" else 0.12, 0.42, 0.23])
    for side in ["left", "top", "right"]:
        ax.spines[side].set_visible(False)
    jan1 = "jan1" if col == "precip" else "jul1"
    c1 = row[f"{col}_record"] or 0
    c2 = max([row[f"{col}_month"] or 0, row[f"{col}_month_normal"] or 0, 0.01])
    c3 = max(
        [row[f"{col}_{jan1}"] or 0, row[f"{col}_{jan1}_normal"] or 0, 0.01]
    )
    ax.bar(
        range(3),
        [
            c1 / max([c1, 0.01]),
            (row[f"{col}_month_normal"] or 0) / c2,
            (row[f"{col}_{jan1}_normal"] or 0) / c3,
        ],
        width=0.3,
        color="tan",
        zorder=8,
    )
    vals = [
        (row[col] or 0) / max([c1, 0.01]),
        (row[f"{col}_month"] or 0) / c2,
        (row[f"{col}_{jan1}"] or 0) / c3,
    ]
    ax.bar(
        range(3),
        vals,
        width=0.2,
        color="b",
        zorder=10,
    )
    ax.text(
        0.2,
        1,
        f"Record: {miss(row[col + '_record'])}\"\n"
        f"{', '.join([str(s) for s in row[col + '_record_years']])}",
        va="center",
        ha="left",
    )
    if not pd.isna(row[col + "_month_normal"]):
        ax.text(
            1.2,
            row[col + "_month_normal"] / c2,
            f"Avg: {miss(row[col + '_month_normal'])}\"",
            va="center",
            ha="left",
        )
    if not pd.isna(row[col + "_" + jan1 + "_normal"]):
        ax.text(
            2.2,
            row[col + "_" + jan1 + "_normal"] / c3,
            f"Avg: {miss(row[col + '_' + jan1 + '_normal'])}\"",
            va="center",
            ha="left",
            bbox=dict(color="white"),
        )
    ax.set_xticks(range(3))
    ax.set_xticklabels(
        [
            f'Day:\n{miss(row[col])}"',
            f"Month:\n{miss(row[col + '_month'])}\"",
            f"Since {jan1.capitalize()}:\n{miss(row[col + '_' + jan1])}\"",
        ],
        fontsize=14,
    )
    ax.set_ylim(0, 1)
    ax.set_yticks([])


def build_params(clsite, dt):
    """Figure out some metrics"""
    hp = GaugeParams()
    lp = GaugeParams()
    if clsite is not None:
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                "SELECT year, high, low from alldata WHERE "
                "station = %s and sday = %s",
                conn,
                params=(clsite, f"{dt:%m%d}"),
                index_col="year",
            )
        hp.minval = df["high"].min()
        hp.maxval = df["high"].max()
        hp.avgval = df["high"].mean()
        hp.stddev = df["high"].std()
        hp.ptiles = df["high"].quantile(np.arange(0.1, 0.91, 0.1)).to_list()
        lp.maxval = df["low"].max()
        lp.minval = df["low"].min()
        lp.avgval = df["low"].mean()
        lp.stddev = df["low"].std()
        lp.ptiles = df["low"].quantile(np.arange(0.1, 0.91, 0.1)).to_list()

    return hp, lp


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            "SELECT * from cli_data where station = %s and valid = %s",
            conn,
            params=(ctx["station"], ctx["date"]),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No CLI data found for date/station.")
    # Build temperature gauge params
    highparams, lowparams = build_params(
        ctx["_nt"].sts[ctx["station"]]["climate_site"],
        ctx["date"],
    )
    row = df.iloc[0]
    title = (
        f"{ctx['date'].strftime('%-d %b %Y')} CLImate Report for "
        f"{ctx['_sname']}"
    )
    fig = figure(title=title, apctx=ctx)

    # High Temp
    fig.text(0.05, 0.85, "High Temperature", fontsize=24)
    if not pd.isna(row["high"]):
        ax = fig.add_axes(
            [0.05, 0.48, 0.3, 0.4],
            projection="polar",
            anchor="SW",
            frame_on=False,
        )
        gauge(ax, row, "high", highparams)

    # Low Temp
    fig.text(0.05, 0.42, "Low Temperature", fontsize=24)
    if not pd.isna(row["low"]):
        ax = fig.add_axes(
            [0.05, 0.05, 0.3, 0.4],
            projection="polar",
            anchor="SW",
            frame_on=False,
        )
        gauge(ax, row, "low", lowparams)

    fig.text(0.05, 0.05, "Lines: Black=Avg, Red=Median, White=10th-90th Ptile")

    fig.text(0.5, 0.85, "Precipitation", fontsize=24)
    precip(fig, row, "precip")

    if row["snow"] is not None or row["snow_month"] is not None:
        fig.text(0.5, 0.42, "Snowfall", fontsize=24)
        precip(fig, row, "snow")

    fig.text(0.3, 0.01, f"Based on text: {row['product']}")
    return fig, df


if __name__ == "__main__":
    plotter({"station": "PBRW", "date": "2023-03-01"})
