""" ASI Data Timeseries """
import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import numpy as np
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def application(environ, start_response):
    """Go Main Go"""
    nt = NetworkTable("ISUASI")
    form = parse_formvars(environ)
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
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR"]

    pgconn = get_dbconn("other")
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    icursor.execute(
        "SELECT * from asi_data WHERE station = %s and "
        "valid BETWEEN %s and %s ORDER by valid ASC",
        (station, sts, ets),
    )
    data = {}
    for i in range(1, 13):
        data[f"ch{i}avg"] = []
    valid = []
    for row in icursor:
        for i in range(1, 13):
            data[f"ch{i}avg"].append(row[f"ch{i}avg"])
        valid.append(row["valid"])

    for i in range(1, 13):
        data[f"ch{i}avg"] = np.array(data[f"ch{i}avg"])

    if len(valid) < 3:
        (_fig, ax) = plt.subplots(1, 1)
        ax.text(0.5, 0.5, "Sorry, no data found!", ha="center")
        start_response("200 OK", [("Content-Type", "image/png")])
        io = BytesIO()
        plt.savefig(io, format="png")
        io.seek(0)
        return [io.read()]

    (_fig, ax) = plt.subplots(2, 1, sharex=True)
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
    central = ZoneInfo("America/Chicago")
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

    ax[0].set_title(f"ISUASI Station: {nt.sts[station]['name']} Timeseries")

    ax[1].plot(valid, data["ch10avg"], color="b", label="3m")
    ax[1].plot(valid, data["ch11avg"], color="r", label="48.5m")
    ax[1].grid(True)
    ax[1].set_ylabel("Air Temperature [C]")
    ax[1].legend(loc="best")

    start_response("200 OK", [("Content-Type", "image/png")])
    io = BytesIO()
    plt.savefig(io, format="png")
    io.seek(0)
    return [io.read()]
