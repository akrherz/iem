"""
This plot compares the month to date average
temperature of this month against any previous month of your choice.
The plot then contains this month's to date average temperature along
with the scenarios of the remaining days for this month from each of
the past years.  These scenarios provide a good approximation of what is
possible for the remainder of the month.
"""

import calendar
import datetime

import numpy as np
from pyiem.database import get_dbconnc
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

PDICT = {
    "manual": "Select comparison month manually",
    "high": "Based on effective date, find warmest same month on record",
    "low": "Based on effective date, find coldest same month on record",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    today = datetime.date.today()
    lastmonth = (today.replace(day=1)) - datetime.timedelta(days=25)
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            network="IACLIMATE",
            label="Select Station:",
        ),
        {
            "type": "select",
            "name": "compare",
            "default": "manual",
            "label": "How to compare?",
            "options": PDICT,
        },
        dict(
            type="year",
            name="year",
            default=lastmonth.year,
            min=1800,
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


def compute_compare_month(ctx, cursor):
    """Figure out what the user wants."""
    year = ctx["year"]
    month = ctx["month"]
    compare = ctx["compare"]
    if compare == "manual":
        return year, month
    station = ctx["station"]
    effective_date = ctx["date"]
    cursor.execute(
        f"""
        select year, avg((high+low)/2) from alldata
        where station = %s and month = %s and year != %s
        and high is not null and low is not null
        GROUP by year
        ORDER by avg {'desc' if compare == 'high' else 'asc'} LIMIT 1
        """,
        (station, effective_date.month, effective_date.year),
    )
    return cursor.fetchone()["year"], effective_date.month


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    pgconn, cursor = get_dbconnc("coop")
    station = ctx["station"]
    effective_date = ctx["date"]
    year, month = compute_compare_month(ctx, cursor)

    oldmonth = datetime.date(year, month, 1)
    sts = datetime.date(effective_date.year, effective_date.month, 1)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    days = int((ets - sts).days)

    # beat month
    cursor.execute(
        "SELECT extract(day from day), (high+low)/2. as t from "
        "alldata WHERE station = %s and year = %s and month = %s "
        "ORDER by day ASC",
        (station, year, month),
    )
    if cursor.rowcount == 0:
        pgconn.close()
        raise NoDataFound("No Data Found.")

    prevmonth = []
    for row in cursor:
        prevmonth.append(float(row["t"]))

    # build history
    cursor.execute(
        "SELECT year, day, (high+low)/2. as t from alldata "
        "WHERE station = %s and month = %s and extract(day from day) <= %s "
        "and day < %s ORDER by day ASC",
        (station, effective_date.month, days, ets),
    )

    for i, row in enumerate(cursor):
        if i == 0:
            baseyear = row["year"]
            data = (
                np.ma.ones((effective_date.year - row["year"] + 1, days)) * -99
            )
        data[row["year"] - baseyear, row["day"].day - 1] = row["t"]
    pgconn.close()
    # Do we have data for the effective_date ?
    pos = (
        effective_date.day
        if data[-1, effective_date.day - 1] > -99
        else (effective_date.day - 1)
    )
    # overwrite our current month's data
    currentdata = data[-1, :pos]
    data[:-1, :pos] = currentdata
    data.mask = data < -98
    avgs = np.ma.zeros(np.shape(data))
    prevavg = []
    for i in range(days):
        avgs[:, i] = np.nanmean(data[:, : i + 1], 1)
        prevavg.append(np.nanmean(prevmonth[: i + 1]))
    avgs.mask = data.mask
    # duplicate the last day for each year, if the value is missing
    for yr in range(np.shape(data)[0] - 1):
        if np.ma.is_masked(avgs[yr, -1]):
            avgs[yr, -1] = avgs[yr, -2]

    beats = 0
    for yr in range(np.shape(data)[0] - 1):
        if avgs[yr, -1] > prevavg[-1]:
            beats += 1
    title = f"{ctx['_sname']} scenarios for {effective_date:%b %Y}"
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

    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)

    for yr in range(np.shape(data)[0] - 1):
        ax.plot(np.arange(1, days + 1), avgs[yr, :], zorder=1, color="tan")

    lv = avgs[-1, pos]
    if np.ma.is_masked(lv):
        lv = avgs[-1, pos - 1]
    ax.plot(
        np.arange(1, pos + 1),
        avgs[-1, :pos],
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
        label=(
            f"{calendar.month_abbr[oldmonth.month]} {oldmonth.year}, "
            f"{prevavg[-1]:.2f}"
            r"$^\circ$F"
        ),
    )

    ax.set_xlim(1, days)
    ax.set_ylabel(r"Month to Date Average Temp $^\circ$F")
    ax.set_xlabel("Day of Month")
    ax.grid(True)
    ax.legend(loc="best", fontsize=10)

    return fig


if __name__ == "__main__":
    plotter({})
