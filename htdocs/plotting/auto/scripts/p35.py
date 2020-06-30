"""x-hour changes."""
import datetime
from collections import OrderedDict
import calendar

import psycopg2.extras
import numpy as np
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    (
        ("tmpf", "Air Temp (F)"),
        ("alti", "Altimeter (in)"),
        ("dwpf", "Dew Point Temp (F)"),
        ("feel", "Feels Like Temp (F)"),
        ("mslp", "Mean Sea Level Pressure (mb)"),
        ("relh", "Relative Humidity (%)"),
    )
)


def compute_bins(interval):
    """ Make even intervals centered around zero"""
    halfsz = interval / 2.0
    multi = int(80.0 / interval)
    v = halfsz + interval * multi
    # print halfsz, multi, v
    return np.arange(0 - v, v + 0.1, interval)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents a histogram of the change
    in some observed variable over a given number of hours."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            options=PDICT,
            default="tmpf",
            name="var",
            label="Select Variable",
        ),
        dict(type="int", name="hours", default=24, label="Hours:"),
        dict(
            type="float",
            name="interval",
            default=1,
            label="Histogram Binning Width (unit of variable)",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    hours = ctx["hours"]
    interval = ctx["interval"]
    varname = ctx["var"]
    if interval > 10 or interval < 0.1:
        raise NoDataFound(
            "Invalid interval provided, positive number less than 10"
        )

    cursor.execute(
        """
    WITH one as (
        select valid, """
        + varname
        + """ as t from alldata where
        station = %s and """
        + varname
        + """ is not null
        ),
        two as (SELECT valid + '%s hours'::interval as v, t from one
        )

    SELECT extract(week from one.valid), two.t - one.t
    from one JOIN two on (one.valid = two.v)
    """,
        (station, hours),
    )
    weeks = []
    deltas = []
    for row in cursor:
        weeks.append(row[0])
        deltas.append(float(row[1]))

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    # We want bins centered on zero
    bins = compute_bins(interval)

    hist, xedges, yedges = np.histogram2d(weeks, deltas, [range(0, 54), bins])
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    years = float(datetime.datetime.now().year - ab.year)
    hist = np.ma.array(hist / years / 7.0)
    hist.mask = np.where(hist < (1.0 / years), True, False)

    (fig, ax) = plt.subplots(1, 1)
    res = ax.pcolormesh((xedges - 1) * 7, yedges, hist.transpose())
    fig.colorbar(res, label="Hours per Day")
    ax.grid(True)
    ax.set_title(
        ("%s [%s] Histogram\n(bin=%s) of %s Hour %s Change")
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            interval,
            hours,
            PDICT[varname],
        )
    )
    ax.set_ylabel("%s Change" % (PDICT[varname],))

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    rng = max([max(deltas), 0 - min(deltas)])
    ax.set_ylim(0 - rng * 1.3, rng * 1.3)

    return fig


if __name__ == "__main__":
    plotter(dict())
