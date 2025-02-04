"""
This plot displays the distribution of observed
daily high and low temperatures for a given day and given state or station.
The
dataset is fit with a simple normal distribution based on the simple
population statistics.
"""

from datetime import datetime

import numpy as np
import pandas as pd
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from scipy.stats import norm

from iemweb.autoplot import ARG_STATION

PDICT = {
    "state": "Plot for a Specific State",
    "station": "Plot for a Specific Station",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        {
            "type": "select",
            "name": "opt",
            "default": "state",
            "label": "Plot all stations in state or single station:",
            "options": PDICT,
        },
        dict(type="state", name="state", default="IA", label="Which state?"),
        ARG_STATION,
        dict(type="month", name="month", default="10", label="Select Month:"),
        dict(type="day", name="day", default="7", label="Select Day:"),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    month = ctx["month"]
    day = ctx["day"]
    ts = datetime(2000, month, day)
    if ctx["opt"] == "station":
        title = f"{ctx['_sname']} {ts:%d %B} Temperature Distribution"
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                sql_helper("""SELECT high, low from alldata
                where station = :station and sday = :sday and high is not null
                and low is not null
                """),
                conn,
                params={
                    "station": ctx["station"],
                    "sday": f"{month:02.0f}{day:02.0f}",
                },
            )
    else:
        state = ctx["state"][:2]
        title = (
            f"{reference.state_names[state]} {ts:%d %B} "
            "Temperature Distribution"
        )
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                sql_helper(
                    """SELECT high, low from {table}
                where sday = :sday and high is not null and low is not null and
                substr(station, 3, 1) != 'T' and
                substr(station, 3, 4) != '0000'
                """,
                    table=f"alldata_{state.lower()}",
                ),
                conn,
                params={"sday": f"{month:02.0f}{day:02.0f}"},
            )
    if df.empty:
        raise NoDataFound("No Data Found.")
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()

    (fig, ax) = figure_axes(title=title, apctx=ctx)

    n, bins, _ = ax.hist(
        highs,
        bins=(np.max(highs) - np.min(highs)),
        histtype="step",
        density=True,
        color="r",
        zorder=1,
    )
    high_freq = pd.Series(n, index=bins[:-1])
    mu, std = norm.fit(highs)
    xmin, xmax = ax.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ax.plot(x, p, "r--", linewidth=2)
    plotted32 = False
    if xmin < 32 < xmax:
        ax.axvline(x=32, color="g", linestyle="--")
        plotted32 = True

    ax.text(
        0.8,
        0.98,
        "\n".join(
            [
                "High Temp\n" rf"$\mu$ = {mu:.1f}$^\circ$F",
                rf"$\sigma$ = {std:.2f}",
                rf"$n$ = {len(highs)}",
            ]
        ),
        va="top",
        ha="left",
        color="r",
        transform=ax.transAxes,
        bbox=dict(color="white"),
    )

    n, bins, _ = ax.hist(
        lows,
        bins=(np.max(lows) - np.min(lows)),
        histtype="step",
        density=True,
        color="b",
        zorder=1,
    )
    low_freq = pd.Series(n, index=bins[:-1])
    df = pd.DataFrame(dict(low_freq=low_freq, high_freq=high_freq))
    df.index.name = "tmpf"
    mu, std = norm.fit(lows)
    xmin, xmax = ax.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ax.plot(x, p, "b--", linewidth=2)
    if xmin < 32 < xmax:
        ax.axvline(x=32, color="g", linestyle="--")
        plotted32 = True

    ax.text(
        0.02,
        0.98,
        "\n".join(
            [
                "Low Temp\n" rf"$\mu$ = {mu:.1f}$^\circ$F",
                rf"$\sigma$ = {std:.2f}",
                rf"$n$ = {len(lows)}",
            ]
        ),
        va="top",
        ha="left",
        color="b",
        transform=ax.transAxes,
        bbox=dict(color="white"),
    )
    ax.grid(True)
    extra = ""
    if plotted32:
        extra = r" (32$^\circ$F highlighted in green)"
    ax.set_xlabel(r"Temperature $^\circ$F" + extra)
    ax.set_ylabel("Probability")

    return fig, df
