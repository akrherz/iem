#!/usr/bin/env python
""" ASI Data Timeseries """
from __future__ import print_function
import sys
import datetime
import cgitb
import cgi

import psycopg2.extras
import pytz
import numpy as np
import matplotlib.dates as mdates

from pyiem.plot.use_agg import plt
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, ssw

cgitb.enable()


def main():
    """Go Main Go"""
    nt = NetworkTable("ISUASI")
    form = cgi.FieldStorage()
    if (
        "syear" in form
        and "eyear" in form
        and "smonth" in form
        and "emonth" in form
        and "sday" in form
        and "eday" in form
        and "shour" in form
        and "ehour" in form
    ):
        sts = datetime.datetime(
            int(form["syear"].value),
            int(form["smonth"].value),
            int(form["sday"].value),
            int(form["shour"].value),
            0,
        )
        ets = datetime.datetime(
            int(form["eyear"].value),
            int(form["emonth"].value),
            int(form["eday"].value),
            int(form["ehour"].value),
            0,
        )
    else:
        sts = datetime.datetime(2012, 12, 1)
        ets = datetime.datetime(2012, 12, 3)

    station = form.getvalue("station", "ISU4003")
    if station not in nt.sts:
        print("Content-type: text/plain\n")
        print("ERROR")
        return

    pgconn = get_dbconn("other")
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """
        SELECT * from asi_data WHERE
        station = '%s' and valid BETWEEN '%s' and '%s' ORDER by valid ASC
    """ % (
        station,
        sts.strftime("%Y-%m-%d %H:%M"),
        ets.strftime("%Y-%m-%d %H:%M"),
    )
    icursor.execute(sql)
    data = {}
    for i in range(1, 13):
        data["ch%savg" % (i,)] = []
    valid = []
    for row in icursor:
        for i in range(1, 13):
            data["ch%savg" % (i,)].append(row["ch%savg" % (i,)])
        valid.append(row["valid"])

    for i in range(1, 13):
        data["ch%savg" % (i,)] = np.array(data["ch%savg" % (i,)])

    if len(valid) < 3:
        (fig, ax) = plt.subplots(1, 1)
        ax.text(0.5, 0.5, "Sorry, no data found!", ha="center")
        print("Content-Type: image/png\n")
        plt.savefig(sys.stdout, format="png")
        return

    (fig, ax) = plt.subplots(2, 1, sharex=True)
    ax[0].grid(True)

    ax[0].plot(
        valid, data["ch1avg"], linewidth=2, color="r", zorder=2, label="48.5m"
    )
    ax[0].plot(
        valid,
        data["ch3avg"],
        linewidth=2,
        color="purple",
        zorder=2,
        label="32m",
    )
    ax[0].plot(
        valid,
        data["ch5avg"],
        linewidth=2,
        color="black",
        zorder=2,
        label="10m",
    )
    ax[0].set_ylabel("Wind Speed [m/s]")
    ax[0].legend(loc=(0.05, -0.15), ncol=3)
    ax[0].set_xlim(min(valid), max(valid))
    days = (max(valid) - min(valid)).days
    central = pytz.timezone("America/Chicago")
    if days >= 3:
        interval = max(int(days / 7), 1)
        ax[0].xaxis.set_major_locator(
            mdates.DayLocator(interval=interval, tz=central)
        )
        ax[0].xaxis.set_major_formatter(
            mdates.DateFormatter("%d %b\n%Y", tz=central)
        )
    else:
        ax[0].xaxis.set_major_locator(
            mdates.AutoDateLocator(maxticks=10, tz=central)
        )
        ax[0].xaxis.set_major_formatter(
            mdates.DateFormatter("%-I %p\n%d %b", tz=central)
        )

    ax[0].set_title(
        "ISUASI Station: %s Timeseries" % (nt.sts[station]["name"],)
    )

    ax[1].plot(valid, data["ch10avg"], color="b", label="3m")
    ax[1].plot(valid, data["ch11avg"], color="r", label="48.5m")
    ax[1].grid(True)
    ax[1].set_ylabel("Air Temperature [C]")
    ax[1].legend(loc="best")

    ssw("Content-Type: image/png\n\n")
    fig.savefig(getattr(sys.stdout, "buffer", sys.stdout), format="png")


if __name__ == "__main__":
    main()
