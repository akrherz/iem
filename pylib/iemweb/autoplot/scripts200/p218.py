"""
This produces an infographic with some of the information found
presented in NWS CLI reports.

<p>The high and low temperature gauges contain some extra statistical
information based on the period of record observations for the site. Sometimes
this period of record information comes from a nearby weather station. This
information also provides the coldest high temperature and warmest low
temperature, both of which are not found within the raw CLI text product.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from math import pi

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot import figure
from pyiem.reference import TRACE_VALUE

TFORMAT = "%b %-d %Y %-I:%M %p %Z"

PDICT = {
    "set": "Use Provided Date.",
    "current": "Use Most Recent Date with Data.",
}


@dataclass
class GaugeParams:
    """Simple."""

    minval: float = None
    maxval: float = None
    avgval: float = None
    stddev: float = None
    ptiles: list = None
    calc_min_high_years: list = None
    calc_max_low_years: list = None
    subtitle: str = None


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 300}
    desc["defaults"] = {"_r": "t"}
    yest = date.today() - timedelta(days=1)
    desc["arguments"] = [
        {
            "type": "select",
            "name": "w",
            "default": "set",
            "label": "Date Selection Method:",
            "options": PDICT,
        },
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


def gauge(ax: Axes, row: dict, col: str, params: GaugeParams):
    """Make the gauge plot."""
    # Override database values with what the CLI has
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
    if positive_delta == 0:
        positive_delta = 0.01
    if negative_delta == 0:
        negative_delta = 0.01
    for val, color, label in zip(bar_ends, colors, labels, strict=False):
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
    # Plot CLI provided record
    ax.text(
        -0.05 if col == "high" else pi + 0.05,
        2,
        f"Record: "
        f"{miss(row[col + '_record'])}°F"
        f"\n{', '.join([str(s) for s in row[col + '_record_years']])}",
        va="top",
        ha="left" if col == "high" else "right",
    )
    # Plot database provided record for that not included in CLI
    dbrecord = params.minval if col == "high" else params.maxval
    dbrecord_years = (
        params.calc_min_high_years
        if col == "high"
        else params.calc_max_low_years
    )
    if dbrecord is not None:
        extra = (
            f"+{len(dbrecord_years) - 3} more"
            if len(dbrecord_years) > 3
            else ""
        )
        ax.text(
            -0.05 if col == "low" else pi + 0.05,
            2,
            f"Record: "
            f"{dbrecord}°F"
            f"\n{', '.join([str(s) for s in dbrecord_years[:3]])}{extra}",
            va="top",
            ha="left" if col == "low" else "right",
        )

    ax.text(
        pi / 2,
        3.25,
        "Avg:\n" + f"{miss(row[f'{col}_normal'])}°F",
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
        f"{row[col]}°F\n@{row[col + '_time']} LST",
        ha="center",
        va="top",
        fontsize=14,
    )


def precip(fig, row, col):
    """Do the precip part."""
    ypos = 0.57 if col == "precip" else 0.11
    ax = fig.add_axes([0.47, ypos, 0.42, 0.23])
    for side in ["left", "top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_alpha(0.35)

    def val_or_zero(value):
        return 0.0 if pd.isna(value) else float(value)

    def ratio_color(ratio, missing_target=False):
        if missing_target:
            return "#9AA5B1"
        if ratio >= 1.05:
            return "#1D7A3A" if col == "precip" else "#2B9EB3"
        if ratio >= 0.85:
            return "#00A3CC" if col == "precip" else "#70B7CF"
        return "#708090"

    def safe_ratio(actual, target):
        if pd.isna(target) or float(target) <= 0:
            return np.nan
        return actual / float(target)

    jan1 = "jan1" if col == "precip" else "jul1"
    actuals = [
        val_or_zero(row[col]),
        val_or_zero(row[f"{col}_month"]),
        val_or_zero(row[f"{col}_{jan1}"]),
    ]
    targets_raw = [
        row[f"{col}_record"],
        row[f"{col}_month_normal"],
        row[f"{col}_{jan1}_normal"],
    ]
    vals = [safe_ratio(actuals[i], targets_raw[i]) for i in range(3)]
    plot_vals = [0 if pd.isna(v) else v for v in vals]
    bar_colors = [
        ratio_color(plot_vals[i], pd.isna(vals[i])) for i in range(3)
    ]

    ymax = max([1.2, np.nanmax(plot_vals) * 1.2])
    ymax = min([ymax, 3.0])

    # A single threshold line keeps the percent-of-target context clear.
    ax.axhline(0.5, color="#94A3B8", linewidth=1.0, alpha=0.35, zorder=1)
    ax.text(
        0.01,
        0.5,
        "50%",
        transform=ax.get_yaxis_transform(),
        va="bottom",
        ha="left",
        fontsize=9,
        color="#64748B",
        alpha=0.8,
    )
    ax.axhline(1.0, color="#2F4858", linewidth=1.8, alpha=0.9, zorder=2)
    ax.text(
        0.01,
        1.0,
        "100%",
        transform=ax.get_yaxis_transform(),
        va="bottom",
        ha="left",
        fontsize=10,
        color="#2F4858",
    )

    bar_cap = ymax * 0.93
    for i, ratio in enumerate(plot_vals):
        bar_height = min([ratio, bar_cap])
        ax.bar(
            i,
            bar_height,
            width=0.42,
            color=bar_colors[i],
            edgecolor="#F7FAFC",
            linewidth=1.2,
            zorder=4,
        )

        if not pd.isna(vals[i]):
            pct_of_target = ratio * 100.0
            ax.text(
                i,
                min([bar_height + 0.06, ymax * 0.97]),
                f"{pct_of_target:.0f}%",
                ha="center",
                va="bottom",
                fontsize=11,
                color=bar_colors[i],
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="white",
                    edgecolor=bar_colors[i],
                    linewidth=1.0,
                ),
                zorder=7,
            )

    years = [str(s) for s in row[col + "_record_years"]]
    suffix = f" (+{len(years) - 2} more)" if len(years) > 2 else ""
    shown_years = ", ".join(years[:2]) if years else "n/a"
    ax.text(
        0.99,
        1.01,
        (
            f'Daily record: {miss(row[col + "_record"])}" '
            f"({shown_years}{suffix})"
        ),
        transform=ax.transAxes,
        va="bottom",
        ha="right",
        fontsize=9,
        color="#374151",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8),
        clip_on=False,
    )

    ax.set_xticks(range(3))
    ax.set_xticklabels(
        [
            (f'Day\nOb {miss(row[col])}" | Max {miss(row[col + "_record"])}"'),
            (
                f"Month\n"
                f'Ob {miss(row[col + "_month"])}" | '
                f'Avg {miss(row[col + "_month_normal"])}"'
            ),
            (
                f"Since {jan1.capitalize()}\n"
                f'Ob {miss(row[col + "_" + jan1])}" | '
                f'Avg {miss(row[col + "_" + jan1 + "_normal"])}"'
            ),
        ],
        fontsize=9,
    )
    ax.tick_params(axis="x", pad=4)
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(0, ymax)
    ax.grid(axis="y", color="#CBD5E1", alpha=0.5, linewidth=0.8)
    ax.set_yticks([])


def build_params(clsite: str, dt: datetime):
    """Figure out some metrics"""
    hp = GaugeParams()
    lp = GaugeParams()
    if clsite is None:
        return hp, lp
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            "SELECT year, high, low from alldata WHERE "
            "station = %s and sday = %s",
            conn,
            params=(clsite, f"{dt:%m%d}"),
            index_col="year",
        )
    if not df.empty:
        hp.minval = df["high"].min()
        hp.maxval = df["high"].max()
        hp.avgval = df["high"].mean()
        hp.stddev = df["high"].std()
        hp.ptiles = df["high"].quantile(np.arange(0.1, 0.91, 0.1)).to_list()
        # These are not provided by the CLI
        hp.calc_min_high_years = df.index[df["high"] == hp.minval].tolist()
        lp.maxval = df["low"].max()
        lp.minval = df["low"].min()
        lp.avgval = df["low"].mean()
        lp.stddev = df["low"].std()
        lp.ptiles = df["low"].quantile(np.arange(0.1, 0.91, 0.1)).to_list()
        # These are not provided by the CLI
        lp.calc_max_low_years = df.index[df["low"] == lp.maxval].tolist()

        # Hacky tagalong
        nt = NetworkTable(f"{clsite[:2]}CLIMATE")
        hp.subtitle = (
            "Auxillary non-CLI stats provided by IEM: "
            f"{nt.sts.get(clsite, {'name': ''})['name']} [{clsite}] "
            f"({df.index.min()}-{df.index.max()})"
        )

    return hp, lp


def get_data(ctx: dict):
    """Get the data."""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            "SELECT * from cli_data where station = %s and valid = %s",
            conn,
            params=(ctx["station"], ctx["date"]),
            index_col=None,
        )
    return df


def plotter(ctx: dict):
    """Go"""
    if ctx["w"] == "current":
        ctx["date"] = date.today()
        df = get_data(ctx)
        if df.empty:
            ctx["date"] -= timedelta(days=1)
            df = get_data(ctx)
            if df.empty:
                raise NoDataFound("No CLI data found for date/station.")
    else:
        df = get_data(ctx)
    if df.empty:
        raise NoDataFound("No CLI data found for date/station.")
    # Build temperature gauge params
    highparams, lowparams = build_params(
        ctx["_nt"].sts[ctx["station"]]["climate_site"],
        ctx["date"],
    )
    row = df.iloc[0]
    has_snow = row["snow"] is not None or row["snow_month"] is not None
    title = (
        f"{ctx['date'].strftime('%-d %b %Y')} CLImate Report for "
        f"{ctx['_sname']}"
    )
    fig = figure(title=title, apctx=ctx, subtitle=highparams.subtitle)

    # High Temp
    fig.text(0.05, 0.85, "High Temperature", fontsize=24)
    if not pd.isna(row["high"]) and highparams.stddev is not None:
        ax = fig.add_axes(
            [0.05, 0.48, 0.3, 0.4],
            projection="polar",
            anchor="SW",
            frame_on=False,
        )
        gauge(ax, row, "high", highparams)

    # Low Temp
    fig.text(0.05, 0.42, "Low Temperature", fontsize=24)
    if not pd.isna(row["low"]) and lowparams.stddev is not None:
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

    if has_snow:
        fig.text(0.5, 0.42, "Snowfall", fontsize=24)
        precip(fig, row, "snow")

    fig.text(0.3, 0.01, f"Based on text: {row['product']}")
    return fig, df
