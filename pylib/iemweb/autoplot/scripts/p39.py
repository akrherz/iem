"""
This plot compares the month to date average
temperature of this month against any previous month of your choice.
The plot then contains this month's to date average temperature along
with the scenarios of the remaining days for this month from each of
the past years.  These scenarios provide a good approximation of what is
possible for the remainder of the month.
"""

import calendar
from datetime import date, timedelta

import numpy as np
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from sqlalchemy.engine import Connection

from iemweb.autoplot import ARG_STATION

PDICT = {
    "manual": "Select comparison month manually",
    "high": "Based on effective date, find warmest same month on record",
    "low": "Based on effective date, find coldest same month on record",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    today = date.today()
    lastmonth = (today.replace(day=1)) - timedelta(days=25)
    desc["arguments"] = [
        ARG_STATION,
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
    res = cursor.execute(
        sql_helper(
            """
        select year, avg((high+low)/2) from alldata
        where station = :station and month = :month and year != :year
        and high is not null and low is not null
        GROUP by year
        ORDER by avg {mydir} LIMIT 1
        """,
            mydir="desc" if compare == "high" else "asc",
        ),
        {
            "station": station,
            "month": effective_date.month,
            "year": effective_date.year,
        },
    )
    return res.fetchone()[0], effective_date.month


@with_sqlalchemy_conn("coop")
def plotter(ctx: dict, conn: Connection | None = None):
    """Go"""
    station = ctx["station"]
    effective_date = ctx["date"]
    year, month = compute_compare_month(ctx, conn)

    oldmonth = date(year, month, 1)
    sts = date(effective_date.year, effective_date.month, 1)
    ets = (sts + timedelta(days=35)).replace(day=1)
    days = int((ets - sts).days)

    # beat month
    res = conn.execute(
        sql_helper(
            "SELECT extract(day from day), (high+low)/2. as t from "
            "alldata WHERE station = :station and year = :year and "
            "month = :month ORDER by day ASC"
        ),
        {"station": station, "year": year, "month": month},
    )
    if res.rowcount == 0:
        raise NoDataFound("No Data Found.")

    prevmonth = [float(row["t"]) for row in res.mappings()]

    # build history
    res = conn.execute(
        sql_helper(
            "SELECT year, day, (high+low)/2. as t from alldata "
            "WHERE station = :station and month = :month and "
            "extract(day from day) <= :days "
            "and day < :ets ORDER by day ASC"
        ),
        {
            "station": station,
            "month": effective_date.month,
            "days": days,
            "ets": ets,
        },
    )

    for i, row in enumerate(res.mappings()):
        if i == 0:
            baseyear = row["year"]
            data = (
                np.ma.ones((effective_date.year - row["year"] + 1, days)) * -99
            )
        data[row["year"] - baseyear, row["day"].day - 1] = row["t"]
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

    lv = avgs[-1, pos - 1]
    if np.ma.is_masked(lv):
        lv = avgs[-1, pos - 2]
    ax.plot(
        np.arange(1, pos + 1),
        avgs[-1, :pos],
        zorder=3,
        lw=2,
        color="brown",
        label=(
            f"{calendar.month_abbr[effective_date.month]} "
            f"{effective_date:%Y}, {lv:.2f}°F"
        ),
    )
    # For historical, we can additionally plot the month values
    today = date.today().replace(day=1)
    if effective_date < today:
        ax.plot(
            np.arange(1, days + 1),
            avgs[-1, :],
            lw=2,
            color="brown",
            linestyle="-.",
            zorder=2,
            label="%s %s Final, %.2f°F"
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
            "°F"
        ),
    )

    ax.set_xlim(1, days)
    ax.set_ylabel("Month to Date Average Temp °F")
    ax.set_xlabel("Day of Month")
    ax.grid(True)
    ax.legend(loc="best", fontsize=10)

    return fig
