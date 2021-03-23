"""Visualization of TAFs"""
import calendar
import datetime
from collections import OrderedDict

# third party
import requests
import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot import get_cmap, figure
from pyiem.util import get_autoplot_context, get_dbconn, drct2text
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 600
    desc[
        "description"
    ] = """
    This app generates infographics for Terminal Aerodome Forecasts (TAF).
    """
    desc["arguments"] = [
        dict(
            type="text",
            default="KENW",
            name="station",
            label="Select station to plot:",
        ),
        dict(
            type="datetime",
            name="valid",
            default="2021/03/23 1720",
            label="TAF Issuance Timestamp (UTC Timestamp):",
            min="1995/01/01 0000",
        ),
    ]
    return desc


def get_text(product_id):
    """get the raw text."""
    text = "Text Unavailable, Sorry."
    uri = f"https://mesonet.agron.iastate.edu/api/1/nwstext/{product_id}"
    try:
        req = requests.get(uri, timeout=5)
        if req.status_code == 200:
            text = req.content.decode("ascii", "ignore").replace("\001", "")
    except Exception:
        pass

    return text


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    valid = ctx["valid"].replace(tzinfo=datetime.timezone.utc)
    pgconn = get_dbconn("asos")
    df = read_sql(
        "SELECT f.*, t.product_id from taf t JOIN taf_forecast f on "
        "(t.id = f.taf_id) WHERE t.station = %s and t.valid = %s "
        "ORDER by f.valid ASC",
        pgconn,
        params=(ctx["station"], valid),
        index_col="valid",
    )
    if df.empty:
        raise NoDataFound("TAF data was not found!")
    title = (
        f"{ctx['station']} Terminal Aerodome Forecast\n"
        f"Valid: {ctx['valid'].strftime('%-d %b %Y %H:%M UTC')}"
    )
    fig = figure(title=title)

    xcols = [0.05, 0.55]
    yrows = [0.4, 0.85]
    gwidth = 0.4
    gheight = 0.32
    ###
    df2 = df[~pd.isna(df["sknt"])]
    sz = len(df2.index)
    xlabels = [s.strftime("%-d/%HZ") for s in df2.index]
    fig.text(xcols[0], yrows[1], "Surface Wind", fontsize=16)
    ax = fig.add_axes([xcols[0], 0.5, gwidth, gheight])
    ax.bar(range(sz), df2["gust"], color="orange", zorder=4, label="Gust")
    ax.bar(range(sz), df2["sknt"], color="blue", zorder=5, label="Sustained")
    ax.legend(ncol=2, bbox_to_anchor=(0.99, 1), loc="lower right")
    ax.grid(True)
    ax.set_ylabel("Wind Speed [kts]")
    ax.set_xticks(range(sz))
    ax.set_xticklabels(xlabels)
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, ymax * 1.3)
    for i, val in enumerate(df2["drct"].values):
        ax.text(
            i,
            ymax * 1.04,
            ("%s\n" r"(%.0f$^\circ$)") % (drct2text(val), val),
            ha="center",
            bbox=dict(color="white"),
        )

    ###
    df2 = df[~pd.isna(df["visibility"])]
    sz = len(df2.index)
    xlabels = [s.strftime("%-d/%HZ") for s in df2.index]
    fig.text(xcols[0], yrows[0], "Visibility", fontsize=16)
    ax = fig.add_axes([xcols[0], 0.07, gwidth, gheight])
    ax.bar(range(sz), df2["visibility"])
    ax.set_xticks(range(sz))
    ax.set_xticklabels(xlabels)
    ax.grid(True)
    ax.set_ylabel("Visibility [miles]")

    ###
    sz = len(df.index)
    xlabels = [s.strftime("%-d/%HZ") for s in df.index]
    fig.text(xcols[1], yrows[1], "Clouds, Weather & Shear", fontsize=16)
    ax = fig.add_axes([xcols[1], 0.5, gwidth, gheight])
    lmax = 10000
    xl = []
    for i, val in enumerate(df["skyc"].values):
        for j, skyc in enumerate(val):
            level = df["skyl"].values[i][j]
            lmax = max([level, lmax])
            ax.text(i, level, skyc, ha="center")
        xl.append(" ".join(df["presentwx"].values[i]) + "\n" + xlabels[i])
        if not pd.isna(df["ws_sknt"].values[i]):
            ax.annotate(
                "WS%03.0f/%02.0f%03.0fKT"
                % (
                    df["ws_level"].values[i] / 100,
                    df["ws_drct"].values[i],
                    df["ws_sknt"].values[i],
                ),
                xy=(i, 1),
                xycoords=("data", "axes fraction"),
                color="blue",
                ha="center",
            )
            ax.axvline(i, color="b")
    ax.set_ylim(0, lmax * 1.2)
    ax.set_xticks(range(sz))
    ax.set_xticklabels(xl)
    ax.set_xlim(-0.5, sz - 0.5)
    ax.grid(axis="y")
    ax.set_ylabel("Cloud Height [ft]")

    ###
    fig.text(xcols[1], yrows[0], "Raw TAF Text", fontsize=16)
    text = get_text(df.iloc[0]["product_id"])
    fig.text(xcols[1] - 0.05, yrows[0], text.strip(), va="top", fontsize=12)
    return fig, df


if __name__ == "__main__":
    plotter(dict())
