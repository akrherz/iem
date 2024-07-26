"""
This plot presents the time series of trailing X
number of day departures evaluated every Y days forward in time.  The
departures are expressed in terms of standard deviation (sigma) by
comparing the current period against the same period of dates back through
the period of record.  The evaluation points are connected by arrows to
express the evolution of the departures.  Since the plot is bounded by
physical processes, the plot tends to cycle.  In economics, a classic
comparable plot to this one is of suply vs demand.
"""

import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

from iemweb.autoplot import ARG_STATION


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="date",
            name="date1",
            default=(today - datetime.timedelta(days=90)).strftime("%Y/%m/%d"),
            label="Start Date:",
            min="1893/01/01",
        ),
        dict(
            type="date",
            name="date2",
            default=today.strftime("%Y/%m/%d"),
            label="End Date (inclusive):",
            min="1893/01/01",
        ),
        dict(
            type="int",
            name="days",
            default="14",
            label="Number of Trailing Days to Use (X)",
        ),
        dict(
            type="int",
            name="days2",
            default="7",
            label="Interval to Compute Trailing Statistics (Y)",
        ),
    ]
    return desc


def get_color(val, cat):
    """get color fpr category and val"""
    if cat == "t":
        if val > 0:
            return "r"
        return "b"
    if val > 0:
        return "b"
    return "r"


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]
    days2 = ctx["days2"]
    date1 = ctx["date1"]
    date2 = ctx["date2"]

    title = (
        f"{ctx['_sname']} ({date1:%d %b %Y} - {date2:%d %b %Y})\n"
        f"{days} Day Trailing Departures plotted every {days2} days"
    )

    (fig, ax) = figure_axes(title=title, apctx=ctx)

    interval = datetime.timedelta(days=days2)

    lbls = []
    lbls2 = []
    psigma = []
    tsigma = []
    aligns = []
    align = ["top", "bottom"]

    now = date1
    while now <= date2:
        sdays = []
        for i in range(0, 0 - days, -1):
            sdays.append((now + datetime.timedelta(days=i)).strftime("%m%d"))  # noqa
        cursor.execute(
            """
        SELECT avg(p), stddev(p), avg(t), stddev(t),
        max(case when year = %s then p else -999 end),
        max(case when year = %s then t else -999 end) from
        (SELECT year, sum(precip) as p, avg((high+low)/2.) as t
        from alldata
        WHERE station = %s and sday = ANY(%s) GROUP by year) as foo
        """,
            (now.year, now.year, station, sdays),
        )
        row = cursor.fetchone()
        if row[0] is None:
            raise NoDataFound("No Data Found.")
        psigma.append((row[4] - row[0]) / row[1])
        tsigma.append((row[5] - row[2]) / row[3])
        lbls.append(now.strftime("%-m/%-d"))
        lbls2.append(now.strftime("%Y-%m-%d"))
        aligns.append(align[now.month % 2])

        now += interval
    pgconn.close()
    df = pd.DataFrame(
        dict(
            psigma=pd.Series(psigma),
            tsigma=pd.Series(tsigma),
            sdate=pd.Series(lbls2),
        )
    )
    tsigma = np.array(tsigma, "f")
    psigma = np.array(psigma, "f")
    ax.quiver(
        tsigma[:-1],
        psigma[:-1],
        tsigma[1:] - tsigma[:-1],
        psigma[1:] - psigma[:-1],
        scale_units="xy",
        angles="xy",
        scale=1,
        zorder=1,
        color="tan",
    )
    for lbl, t, p, a in zip(lbls, tsigma, psigma, aligns):
        # Manual move label some for readiability
        if lbl == "7/15":
            t = float(t) + 0.1
            p = float(p) + -0.2
        ax.text(t, p, lbl, va=a, zorder=2)

    tmax = max([abs(np.min(tsigma)), abs(np.max(tsigma))]) + 0.5
    ax.set_xlim(0 - tmax, tmax)
    pmax = max([abs(np.min(psigma)), abs(np.max(psigma))]) + 0.5
    ax.set_ylim(0 - pmax, pmax)
    ax.set_ylabel(r"Precipitation Departure $\sigma$")
    ax.set_xlabel(r"Temperature Departure $\sigma$")
    ax.grid(True)
    ax.set_position([0.1, 0.1, 0.7, 0.8])
    y = 0.96
    pos = [1.01, 1.15, 1.22]
    ax.text(pos[0], y + 0.04, "Date", transform=ax.transAxes, fontsize=10)
    ax.text(
        pos[1],
        y + 0.04,
        r"T $\sigma$",
        transform=ax.transAxes,
        fontsize=10,
        ha="right",
    )
    ax.text(
        pos[2],
        y + 0.04,
        r"P $\sigma$",
        transform=ax.transAxes,
        fontsize=10,
        ha="right",
    )
    for lbl, t, p in zip(lbls, tsigma, psigma):
        ax.text(pos[0], y, f"{lbl}", transform=ax.transAxes, fontsize=10)
        ax.text(
            pos[1],
            y,
            f"{t:.1f}",
            transform=ax.transAxes,
            fontsize=10,
            color=get_color(t, "t"),
            ha="right",
        )
        ax.text(
            pos[2],
            y,
            f"{p:.1f}",
            transform=ax.transAxes,
            fontsize=10,
            color=get_color(p, "p"),
            ha="right",
        )
        y -= 0.04
    return fig, df
