"""
This autoplot attempts to provide probabilities of some month/year besting
some previous month/year.  These probabilities are built by appending all
previous years on record onto the current month to date or year to date
value.  The theory is that the past provides an envelope of what is possible
for the future.  This autoplot is not an exact science as leap days and other
calendar quirks can make an off-by-one situation with the data comparisons.
"""

from calendar import month_name, monthrange
from datetime import date, timedelta

import numpy as np
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from sqlalchemy.engine import Connection

from iemweb.autoplot import ARG_STATION

PDICT = {
    "manual": "Select comparison month/year manually",
    "high": "Based on effective date, find maximum record for same month/year",
    "low": "Based on effective date, find minimum record for same month/year",
}
PDICT2 = {
    "month": "Create scenarios for given month",
    "year": "Create scenarios for given year",
}
VDICT = {
    "avg_temp": "Average Temperature",
    "total_precip": "Total Precipitation",
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
            "name": "which",
            "default": "month",
            "label": "Scenario Type",
            "options": PDICT2,
        },
        {
            "type": "select",
            "options": VDICT,
            "name": "var",
            "label": "Variable to Plot",
            "default": "avg_temp",
        },
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
            label="Effective Date (Can not be Feb 29th, sorry).",
        ),
    ]
    return desc


def compute_comparison(ctx: dict, cursor):
    """Figure out what the user wants."""
    year = ctx["year"]
    month = ctx["month"]
    compare = ctx["compare"]
    if compare == "manual":
        return year, month
    station = ctx["station"]
    effective_date = ctx["date"]
    valid_condition = (
        "high is not null and low is not null"
        if compare == "high"
        else "precip is not null"
    )
    month_limit = "" if ctx["which"] == "year" else "and month = :month"
    res = cursor.execute(
        sql_helper(
            """
        select year, avg((high+low)/2) as avg_temp,
        sum(precip) as total_precip from alldata
        where station = :station {month_limit} and year != :year
        and {valid_condition}
        GROUP by year
        ORDER by {varname} {mydir} LIMIT 1
        """,
            mydir="desc" if compare == "high" else "asc",
            varname=ctx["var"],
            valid_condition=valid_condition,
            month_limit=month_limit,
        ),
        {
            "station": station,
            "month": effective_date.month,
            "year": effective_date.year,
        },
    )
    row = res.fetchone()
    if row is None:
        raise NoDataFound("Failed to dynamically compute comparison year")
    return row[0], 1 if ctx["which"] == "year" else effective_date.month


@with_sqlalchemy_conn("coop")
def plotter(ctx: dict, conn: Connection | None = None):
    """Go"""
    # This is when scenarios are used to construct the to date stats
    scenario_start_date: date = ctx["date"]
    if scenario_start_date.strftime("%m%d") == "0229":
        raise NoDataFound("Leap day data is not supported.")
    station = ctx["station"]
    # Figure out the comparison year and month based on the context
    comparison_year, comparison_month = compute_comparison(ctx, conn)

    # These are inclusive start and end dates used for data loading.
    sts = date(
        scenario_start_date.year,
        1 if ctx["which"] == "year" else scenario_start_date.month,
        1,
    )
    inclusive_ets = date(
        scenario_start_date.year,
        12 if ctx["which"] == "year" else scenario_start_date.month,
        monthrange(
            scenario_start_date.year,
            12 if ctx["which"] == "year" else scenario_start_date.month,
        )[1],
    )
    month_limiter = "and month = :month"
    if ctx["which"] == "year":
        month_limiter = ""

    col = "t" if ctx["var"] == "avg_temp" else "p"

    # comparison to beat
    res = conn.execute(
        sql_helper(
            """
    SELECT sday, (high+low)/2. as t, precip as p from
    alldata WHERE station = :station and year = :year {month_limiter}
    ORDER by day ASC""",
            month_limiter=month_limiter,
        ),
        {
            "station": station,
            "year": comparison_year,
            "month": comparison_month,
        },
    )
    comparison_obs = [float(row[col]) for row in res.mappings()]

    # Figure out the x-size of the storage array
    days = int((inclusive_ets - sts).days) + 1
    # If we have leap day involved, extend by one
    if sts.month == 1 and days > 100:
        days += 1

    # observed values, which can not include the scenario start date.
    res = conn.execute(
        sql_helper(
            """
    SELECT sday, (high+low)/2. as t, precip as p from
    alldata WHERE station = :station and year = :year {month_limiter}
    and day < :dt
    ORDER by day ASC""",
            month_limiter=month_limiter,
        ),
        {
            "station": station,
            "year": scenario_start_date.year,
            "month": scenario_start_date.month,
            "dt": scenario_start_date,
        },
    )
    observed = [float(row[col]) for row in res.mappings()]

    # build history for the scenario_start_date, which can not include this yr
    res = conn.execute(
        sql_helper(
            """
    SELECT year, day, (high+low)/2. as t, precip as p from alldata
    WHERE station = :station and sday >= :sdate and sday <= :edate
    and year < :last_year
    ORDER by day ASC"""
        ),
        {
            "station": station,
            "sdate": scenario_start_date.strftime("%m%d"),
            "edate": inclusive_ets.strftime("%m%d"),
            "last_year": scenario_start_date.year,
        },
    )

    data = None
    for i, row in enumerate(res.mappings()):
        # The first row will tell us how to size the data array
        if i == 0:
            baseyear = row["year"]
            data = (
                np.ma.ones((scenario_start_date.year - row["year"] + 1, days))
                * -99
            )
        offset = (row["day"] - sts.replace(year=row["year"])).days
        data[row["year"] - baseyear, offset] = row[col]
    if data is None:
        raise NoDataFound("Failed to find observed data")

    # Replace each year of data with the observed values
    for yr in range(data.shape[0]):
        data[yr, : len(observed)] = observed
        # Repeat the last column, meh
        if data[yr, -1] == -99:
            data[yr, -1] = data[yr, -2]

    # Set anything with -99 sentinel value as masked
    data.mask = data < -98
    cumstat = np.ma.zeros(np.shape(data))
    comparison_cumstat = []
    func = np.nanmean if ctx["var"] == "avg_temp" else np.nansum
    for i in range(days):
        cumstat[:, i] = func(data[:, : i + 1], 1)
        comparison_cumstat.append(func(comparison_obs[: i + 1]))
    cumstat.mask = data.mask

    years = np.shape(data)[0]
    beats = 0
    for yr in range(years):
        if cumstat[yr, -1] > comparison_cumstat[-1]:
            beats += 1
    title = f"{ctx['_sname']} Historical Scenarios"
    freq = beats / float(years) * 100.0
    edate = scenario_start_date - timedelta(days=1)
    labelbeats = f"{comparison_year}"
    if ctx["which"] == "month":
        labelbeats += f" {month_name[comparison_month]}"
    subtitle = (
        f"Obs:{sts:%b %-d}-{edate:%b %-d} {scenario_start_date:%Y} + "
        f"Scenarios: {scenario_start_date:%b %-d}-{inclusive_ets:%b %-d} "
        f"[{baseyear}-{scenario_start_date.year - 1}] "
        f"beats {labelbeats} ({beats}/{years} {freq:.1f}%)"
    )

    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)

    xaxis = pd.date_range(start=sts, periods=days)

    for yr in range(years):
        ax.plot(xaxis, cumstat[yr, :], zorder=1, color="tan")

    units = "°F" if ctx["var"] == "avg_temp" else "in"
    if observed:
        observed_cum = [func(observed[: i + 1]) for i in range(len(observed))]
        ax.plot(
            pd.date_range(start=sts, periods=len(observed_cum)),
            observed_cum,
            zorder=3,
            lw=2,
            color="brown",
            label=f"{sts:%Y}, {observed_cum[-1]:.2f}{units}",
        )
    comparison_cum = [
        func(comparison_obs[: i + 1]) for i in range(len(comparison_obs))
    ]
    complabel = (
        "" if ctx["which"] == "year" else f" {month_name[comparison_month]}"
    )
    # This ensures the plot looks OK, alas, undefined param space if these
    # do not align
    compdays = min(len(comparison_cum), days)
    ax.plot(
        pd.date_range(start=sts, periods=compdays),
        comparison_cum[:compdays],
        lw=2,
        color="brown",
        linestyle="-.",
        zorder=2,
        label=(
            f"{comparison_year}{complabel}, {comparison_cum[-1]:.2f}{units}"
        ),
    )

    label_day_of_months = [1, 8, 15, 22, 29]
    if days > 45:
        label_day_of_months = [1]
    xlabels = []
    xticks = []
    for dt in pd.date_range(start=sts, periods=days):
        if dt.day in label_day_of_months:
            xlabels.append(f"{dt:%b %-d}")
            xticks.append(dt)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)
    ax.set_ylabel(f"To Date {VDICT[ctx['var']]} {units}")
    ax.set_xlabel("Date")
    ax.grid(True)
    ax.legend(loc="best", fontsize=10)

    return fig
