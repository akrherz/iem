"""precip bias by hour"""
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
import pytz
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """
    This plot looks at the bias associated with computing
    24 hour precipitation totals using a given hour of the day as the
    delimiter. This plot will take a number of seconds to generate, so please
    be patient.  This chart attempts to address the question of if computing
    24 hour precip totals at midnight or 7 AM biases the totals.  Such biases
    are commmon when computing this metric for high or low temperature."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        )
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    jan1 = datetime.datetime.now().replace(
        hour=0,
        day=1,
        month=1,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=pytz.utc,
    )
    ts1973 = datetime.datetime(1973, 1, 1)
    today = datetime.datetime.now()
    cursor.execute(
        "SELECT valid at time zone 'UTC', phour from hourly WHERE "
        "iemid = %s and phour > 0.009 and "
        "valid >= '1973-01-01 00:00+00' and valid < %s",
        (ctx["_nt"].sts[station]["iemid"], jan1),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")

    days = (jan1.year - 1973) * 366
    data = np.zeros((days * 24), "f")
    minvalid = today
    for row in cursor:
        if row[0] < minvalid:
            minvalid = row[0]
        data[(row[0] - ts1973).days * 24 + row[0].hour] = row[1]

    lts = jan1.astimezone(pytz.timezone(ctx["_nt"].sts[station]["tzname"]))
    lts = lts.replace(month=7, hour=0)
    cnts = [0] * 24
    avgv = [0] * 24
    rows = []
    for hr in range(24):
        ts = lts.replace(hour=hr)
        zhour = ts.astimezone(pytz.utc).hour
        arr = np.reshape(data[zhour : (0 - 24 + zhour)], (days - 1, 24))
        tots = np.sum(arr, 1)
        cnts[hr] = np.sum(np.where(tots > 0, 1, 0))
        avgv[hr] = np.average(tots[tots > 0])
        rows.append(
            dict(
                average_precip=avgv[hr],
                events=cnts[hr],
                zhour=zhour,
                localhour=hr,
            )
        )

    df = pd.DataFrame(rows)
    title = (
        f"{ctx['_sname']} ({minvalid.year}-{datetime.date.today().year})\n"
        "Bias of 24 Hour 'Day' Split for Precipitation"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    acount = np.average(cnts)
    years = today.year - minvalid.year
    arc = (np.array(cnts) - acount) / float(years)
    maxv = max([0 - np.min(arc), np.max(arc)])
    line = ax.plot(range(24), arc, color="b", label="Days Bias")
    ax.set_ylim(0 - maxv - 0.2, maxv + 0.2)

    ax2 = ax.twinx()
    aavg = np.average(avgv)
    aavgv = np.array(avgv) - aavg
    l2 = ax2.plot(range(24), aavgv, color="r")
    maxv = max([0 - np.min(aavgv), np.max(aavgv)])
    ax2.set_ylim(0 - maxv - 0.01, maxv + 0.01)
    ax2.set_ylabel("Bias with Average 24 Hour Precip [in/day]", color="r")
    ax.set_ylabel("Bias of Days per Year with Precip", color="b")
    ax.set_xlim(0, 24)
    ax.set_xticks((0, 4, 8, 12, 16, 20, 24))
    ax.set_xticklabels(("Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM", "Mid"))
    ax.grid(True)
    ax.set_xlabel(
        "Hour Used for 24 Hour Summary, "
        f"Timezone: {ctx['_nt'].sts[station]['tzname']}"
    )
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.95, box.height])
    ax2.set_position([box.x0, box.y0, box.width * 0.95, box.height])
    ax.legend(
        [line[0], l2[0]],
        ["Days Bias", "Avg Precip Bias"],
        loc="best",
        fontsize=10,
    )
    return fig, df


if __name__ == "__main__":
    plotter({})
