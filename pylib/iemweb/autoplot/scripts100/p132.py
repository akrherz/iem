"""
This plot displays the top ten events for a given
site and period of your choice. Here is a description of the labels
shown in the 'Which Metric to Summarize' option:
<ul>
    <li><i>Total Precipitation</i>: Total precipitation over the specified
    number of days.</li>
    <li><i>Total Snowfall</i>: Total snowfall over the specified
    number of days.</li>
    <li><i>Max Least High</i>: The highest minimum high temperature over
    the specified duration of days.</li>
<li><i>Min Greatest Low</i>: The coldest maximum low temperature over
    the specified duration of days. Example series) -15 -12 -14 -16 would
    be -12</li>
</ul>
"""

import calendar
from datetime import datetime, timedelta

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION
from iemweb.util import month2months

MDICT = {
    "all": "Entire Year",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "octmar": "October thru March",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
PDICT = {
    "daily": "Compute Daily Totals",
    "monthly": "Compute Monthly Totals",
}

METRICS = {
    "total_precip": "Total Precipitation",
    "total_snowfall": "Total Snowfall",
    "max_least_high": "Max Least High",
    "min_greatest_low": "Min Greatest Low",
}
TRANSLATION = {
    "total_precip": "Precipitation",
    "total_snowfall": "Snowfall",
    "max_least_high": "Max High Temperature",
    "min_greatest_low": "Min Low Temperature",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="var",
            default="total_precip",
            label="Which Metric to Summarize",
            options=METRICS,
        ),
        {
            "type": "select",
            "name": "period",
            "default": "daily",
            "label": "Period for Computation",
            "options": PDICT,
        },
        dict(
            type="int",
            name="days",
            default=1,
            label="Over how many consecutive days (ignored for monthly)",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
    ]
    return desc


def get_dataframe(ctx: dict) -> pd.DataFrame:
    """Figure out what we want from the database."""
    varname = ctx["var"]
    station = ctx["station"]
    days = ctx["days"]
    month = ctx["month"]
    months = month2months(month)
    sorder = "ASC" if varname == "min_greatest_low" else "DESC"
    sql = """
        WITH data as (
            SELECT month, day, day - ':days days'::interval as start_date,
            count(*) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as count,
            sum(precip) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as total_precip,
            sum(snow) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as total_snowfall,
            min(high) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as max_least_high,
            max(low) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as min_greatest_low
            from alldata WHERE station = :station)

        SELECT day as end_date, start_date, {varname} from data WHERE
        month = ANY(:months) and
        extract(month from start_date) = ANY(:months) and count = :d2 and
        {varname} is not null
        ORDER by {varname} {sorder} LIMIT 10
    """
    yearagg = "year"
    if ctx["period"] == "monthly":
        if month == "winter":
            yearagg = "case when month = 12 then year + 1 else year end"
        sql = """
    with data as (
        select {yearagg} as ya, min(day) as start_date, max(day) as end_date,
        count(*) as count,
        sum(precip) as total_precip,
        sum(snow) as total_snowfall,
        min(high) as max_least_high,
        max(low) as min_greatest_low
        from alldata WHERE station = :station and month = ANY(:months)
        GROUP by ya
    )
        select ya as year, start_date, end_date, {varname} from data WHERE
        {varname} is not null
        ORDER by {varname} {sorder} LIMIT 10
        """
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(sql, yearagg=yearagg, varname=varname, sorder=sorder),
            conn,
            params={
                "days": days - 1,
                "station": station,
                "months": months,
                "d2": days,
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("Error, no results returned!")
    return df


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    month = ctx["month"]
    varname = ctx["var"]
    days = ctx["days"]

    df = get_dataframe(ctx)
    ylabels = []
    fmt = "%.2f" if varname == "total_precip" else "%.0f"
    if varname == "total_snowfall":
        fmt = "%.1f"
    for _, row in df.iterrows():
        # no strftime support for old days, so we hack at it
        lbl = fmt % (row[varname],)
        if ctx["period"] == "monthly":
            if row["start_date"].month == row["end_date"].month:
                lbl += (
                    f" -- {calendar.month_abbr[row['end_date'].month]} "
                    f"{row['end_date'].year}"
                )
            else:
                lbl += (
                    f" -- {calendar.month_abbr[row['start_date'].month]} "
                    f"{row['start_date'].year} to "
                    f"{calendar.month_abbr[row['end_date'].month]} "
                    f"{row['end_date'].year}"
                )
        elif days > 1:
            sts = row["end_date"] - timedelta(days=days - 1)
            if sts.month == row["end_date"].month:
                lbl += " -- %s %s-%s, %s" % (
                    calendar.month_abbr[sts.month],
                    sts.day,
                    row["end_date"].day,
                    sts.year,
                )
            else:
                lbl += " -- %s %s, %s to\n          %s %s, %s" % (
                    calendar.month_abbr[sts.month],
                    sts.day,
                    sts.year,
                    calendar.month_abbr[row["end_date"].month],
                    row["end_date"].day,
                    row["end_date"].year,
                )
        else:
            lbl += " -- %s %s, %s" % (
                calendar.month_abbr[row["end_date"].month],
                row["end_date"].day,
                row["end_date"].year,
            )
        ylabels.append(lbl)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    tt = f"{METRICS[varname]} [days={days}]"
    if days == 1:
        tt = f"Single Day {TRANSLATION[varname]}"
    title = f"{ctx['_sname']}:: Top 10 Events"
    subtitle = f"{tt} ({MDICT[month]}) ({ab.year}-{datetime.now().year})"
    if ctx["period"] == "monthly":
        title = f"{ctx['_sname']}:: Top 10 Monthly"
        subtitle = (
            f"{METRICS[varname]} ({MDICT[month]}) "
            f"({ab.year}-{datetime.now().year})"
        )

    fig = figure(apctx=ctx, title=title, subtitle=subtitle)
    ax = fig.add_axes((0.1, 0.1, 0.5, 0.8))
    ax.barh(
        range(len(df.index), 0, -1),
        df[varname],
        ec="green",
        fc="green",
        height=0.8,
        align="center",
    )
    ax2 = ax.twinx()
    ax2.set_ylim(0.5, 10.5)
    ax.set_ylim(0.5, 10.5)
    ax2.set_yticks(range(1, 11))
    ax.set_yticks(range(1, 11))
    ax.set_yticklabels(["#%s" % (x,) for x in range(1, 11)][::-1])
    ax2.set_yticklabels(ylabels[::-1])
    ax.grid(True, zorder=11)
    xlabel = "Precipitation [inch]"
    if varname in ["max_least_high", "min_greatest_low"]:
        xlabel = "Temperature [°F]"
    elif varname == "total_snowfall":
        xlabel = "Snowfall [inch]"
    ax.set_xlabel(xlabel)

    return fig, df
