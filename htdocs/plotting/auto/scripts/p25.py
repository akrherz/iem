"""Distrubution of daily high and low temperatures"""
import datetime

import psycopg2.extras
import numpy as np
from scipy.stats import norm
import pandas as pd
from pyiem import reference
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot displays the distribution of observed
    daily high and low temperatures for a given day and given state.  The
    dataset is fit with a simple normal distribution based on the simple
    population statistics.
    """
    desc["arguments"] = [
        dict(type="state", name="state", default="IA", label="Which state?"),
        dict(type="month", name="month", default="10", label="Select Month:"),
        dict(type="day", name="day", default="7", label="Select Day:"),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop", user="nobody")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())

    month = ctx["month"]
    day = ctx["day"]
    state = ctx["state"][:2]
    table = "alldata_%s" % (state,)
    cursor.execute(
        f"SELECT high, low from {table} where sday = %s and high is not null "
        "and low is not null",
        ("%02i%02i" % (month, day),),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")
    highs = []
    lows = []
    for row in cursor:
        highs.append(row[0])
        lows.append(row[1])
    highs = np.array(highs)
    lows = np.array(lows)

    (fig, ax) = plt.subplots(1, 1)

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
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ax.plot(x, p, "r--", linewidth=2)

    ax.text(
        0.8,
        0.98,
        "\n".join(
            [
                rf"High Temp\n$\mu$ = {mu:.1f}$^\circ$F",
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
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ax.plot(x, p, "b--", linewidth=2)

    ts = datetime.datetime(2000, month, day)
    ax.set_title(
        ("%s %s Temperature Distribution")
        % (reference.state_names[state], ts.strftime("%d %B"))
    )

    ax.text(
        0.02,
        0.98,
        "\n".join(
            [
                rf"Low Temp\n$\mu$ = {mu:.1f}$^\circ$F",
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
    ax.set_xlabel(r"Temperature $^\circ$F")
    ax.set_ylabel("Probability")

    return fig, df


if __name__ == "__main__":
    plotter(dict())
