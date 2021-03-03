"""scenarios"""
import datetime
import calendar

import psycopg2.extras
import numpy as np
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc[
        "description"
    ] = """This plot compares the month to date average
    temperature of this month against any previous month of your choice.
    The plot then contains this month's to date average temperature along
    with the scenarios of the remaining days for this month from each of
    the past years.  These scenarios provide a good approximation of what is
    possible for the remainder of the month."""
    today = datetime.date.today()
    lastmonth = (today.replace(day=1)) - datetime.timedelta(days=25)
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            network="IACLIMATE",
            label="Select Station:",
        ),
        dict(
            type="year",
            name="year",
            default=lastmonth.year,
            min=1893,
            label="Select Year to Compare With:",
        ),
        dict(
            type="month",
            name="month",
            default=lastmonth.month,
            label="Select Month to Compare With:",
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            min="1893/01/01",
            label="Effective Date",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    year = ctx["year"]
    month = ctx["month"]
    effective_date = ctx["date"]
    table = "alldata_%s" % (station[:2],)

    oldmonth = datetime.date(year, month, 1)
    sts = datetime.date(effective_date.year, effective_date.month, 1)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    days = int((ets - sts).days)

    # beat month
    cursor.execute(
        f"SELECT extract(day from day), (high+low)/2. from {table} "
        "WHERE station = %s and year = %s and month = %s "
        "ORDER by day ASC",
        (station, year, month),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")

    prevmonth = []
    for row in cursor:
        prevmonth.append(float(row[1]))

    # build history
    cursor.execute(
        f"SELECT year, day, (high+low)/2. from {table} WHERE station = %s "
        "and month = %s and extract(day from day) <= %s and day < %s "
        "ORDER by day ASC",
        (station, effective_date.month, days, ets),
    )

    for i, row in enumerate(cursor):
        if i == 0:
            baseyear = row[0]
            data = np.ma.ones((effective_date.year - row[0] + 1, days)) * -99
        data[row[0] - baseyear, row[1].day - 1] = row[2]

    # overwrite our current month's data
    currentdata = data[-1, : effective_date.day - 1]
    for i in range(np.shape(data)[0] - 1):
        data[i, : effective_date.day - 1] = currentdata
    data.mask = data < -98
    avgs = np.ma.zeros(np.shape(data))
    days = np.shape(data)[1]
    prevavg = []
    for i in range(days):
        avgs[:, i] = np.sum(data[:, : i + 1], 1) / float(i + 1)
        prevavg.append(np.sum(prevmonth[: i + 1]) / float(i + 1))
    avgs.mask = data.mask

    beats = 0
    for yr in range(np.shape(data)[0] - 1):
        if avgs[yr, -1] > prevavg[-1]:
            beats += 1
    title = "[%s] %s scenarios for %s" % (
        station,
        ctx["_nt"].sts[station]["name"],
        effective_date.strftime("%b %Y"),
    )
    subtitle = "1-%s [%s] + %s-%s [%s-%s] beats %s %s %s/%s (%.1f%%)" % (
        effective_date.day,
        effective_date.year,
        effective_date.day + 1,
        days,
        baseyear,
        effective_date.year - 1,
        calendar.month_abbr[oldmonth.month],
        oldmonth.year,
        beats,
        np.shape(data)[0] - 1,
        beats / float(np.shape(data)[0] - 1) * 100.0,
    )

    (fig, ax) = figure_axes(title=title, subtitle=subtitle)

    for yr in range(np.shape(data)[0] - 1):
        ax.plot(np.arange(1, days + 1), avgs[yr, :], zorder=1, color="tan")

    lv = avgs[-1, effective_date.day - 1]
    if np.ma.is_masked(lv):
        lv = avgs[-1, effective_date.day - 2]
    ax.plot(
        np.arange(1, effective_date.day),
        avgs[-1, : effective_date.day - 1],
        zorder=3,
        lw=2,
        color="brown",
        label=r"%s %s, %.2f$^\circ$F"
        % (calendar.month_abbr[effective_date.month], effective_date.year, lv),
    )
    # For historical, we can additionally plot the month values
    today = datetime.date.today().replace(day=1)
    if effective_date < today:
        ax.plot(
            np.arange(1, days + 1),
            avgs[-1, :],
            lw=2,
            color="brown",
            linestyle="-.",
            zorder=2,
            label=r"%s %s Final, %.2f$^\circ$F"
            % (
                calendar.month_abbr[effective_date.month],
                effective_date.year,
                avgs[-1, -1],
            ),
        )
    ax.plot(
        np.arange(1, len(prevavg) + 1),
        prevavg,
        lw=2,
        color="k",
        zorder=3,
        label=r"%s %s, %.2f$^\circ$F"
        % (calendar.month_abbr[oldmonth.month], oldmonth.year, prevavg[-1]),
    )

    ax.set_xlim(1, days)
    ax.set_ylabel(r"Month to Date Average Temp $^\circ$F")
    ax.set_xlabel("Day of Month")
    ax.grid(True)
    ax.legend(loc="best", fontsize=10)

    return fig


if __name__ == "__main__":
    plotter(dict(station="IA0200", network="IACLIMATE"))
