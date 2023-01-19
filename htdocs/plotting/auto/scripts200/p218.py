"""Fancy pants visualization of CLI data."""
# Local
from datetime import date, timedelta
from math import pi

# third party
import numpy as np
import pandas as pd
from pyiem.reference import TRACE_VALUE
from pyiem.network import Table as NetworkTable
from pyiem.plot import figure, get_cmap
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, LOG
from pyiem.exceptions import NoDataFound

TFORMAT = "%b %-d %Y %-I:%M %p %Z"


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["defaults"] = {"_r": "t"}
    # Shorten the cache as CLIs sometimes get updated frequently.
    desc["cache"] = 300
    desc["data"] = True
    desc[
        "description"
    ] = """This produces an infographic with some of the information found
    presented in NWS CLI reports.
    """
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


def gauge(ax, row, col):
    """Make the gauge plot."""
    cmap = get_cmap("RdBu")
    rad = np.arange(0, 3)
    az = np.arange(0, pi + 0.025, 0.025)
    rad, az = np.meshgrid(rad, az)
    z = az / pi
    ax.grid(False)
    ax.pcolormesh(
        az,
        rad,
        z,
        cmap=cmap,
        shading="auto",
    )
    ax.set_xlim(0, pi)
    ax.set_xticks([])
    maxval = row[f"{col}_record"]
    normal = row[f"{col}_normal"]
    if pd.isna(normal):
        normal = row[col]
    if pd.isna(maxval):
        maxval = normal + (20 if col == "high" else -20)
    minval = normal - (maxval - normal)
    ratio = (row[col] - minval) / (maxval - minval)
    if col == "high":
        ratio = 1 - ratio
    if ratio < 0:
        ratio = 0
    elif ratio > 1:
        ratio = 1
    theta = ratio * pi
    ax.text(
        0 if col == "high" else pi,
        3.25,
        f"Record:\n"
        rf"{miss(row[col + '_record'])}$^\circ$F"
        f"\n{', '.join([str(s) for s in row[col + '_record_years']])}",
        va="center",
        ha="left" if col == "high" else "right",
    )
    ax.text(
        pi / 2,
        3.25,
        rf"Avg: {miss(row[f'{col}_normal'])}$^\circ$F",
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
    # ax.text(0, vals[0] + 0.04, str(row[col]), ha="center")
    # ax.text(1, vals[1] + 0.04, str(row[col + "_month"]), ha="center")
    # ax.text(2, vals[2] + 0.04, str(row[col + "_" + jan1]), ha="center")
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


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    nt = NetworkTable("NWSCLI")
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            "SELECT * from cli_data where station = %s and valid = %s",
            conn,
            params=(ctx["station"], ctx["date"]),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No CLI data found for date/station.")
    row = df.iloc[0]
    title = (
        f"{ctx['date'].strftime('%-d %b %Y')} CLImate Report for "
        f"{ctx['station']} {nt.sts[ctx['station']]['name']}"
    )
    fig = figure(title=title, apctx=ctx)

    # High Temp
    fig.text(0.05, 0.85, "High Temperature", fontsize=24)
    if not pd.isna(row["high"]):
        ax = fig.add_axes(
            [0.05, 0.48, 0.3, 0.4],
            projection="polar",
            anchor="SW",
        )
        try:
            gauge(ax, row, "high")
        except Exception as exp:
            LOG.exception(exp)

    # Low Temp
    fig.text(0.05, 0.42, "Low Temperature", fontsize=24)
    if not pd.isna(row["low"]):
        ax = fig.add_axes(
            [0.05, 0.05, 0.3, 0.4],
            projection="polar",
            anchor="SW",
        )
        try:
            gauge(ax, row, "low")
        except Exception as exp:
            LOG.exception(exp)

    fig.text(0.5, 0.85, "Precipitation", fontsize=24)
    try:
        precip(fig, row, "precip")
    except Exception as exp:
        LOG.exception(exp)

    if row["snow"] is not None or row["snow_month"] is not None:
        fig.text(0.5, 0.42, "Snowfall", fontsize=24)
        try:
            precip(fig, row, "snow")
        except Exception as exp:
            LOG.exception(exp)

    fig.text(0.3, 0.01, f"Based on text: {row['product']}")
    return fig, df


if __name__ == "__main__":
    plotter({"station": "KUKI", "date": "2021-03-28"})
