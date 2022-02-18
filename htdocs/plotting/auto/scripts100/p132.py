"""Top 10"""
import datetime
import calendar

import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

MDICT = dict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("octmar", "October thru March"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)

METRICS = dict(
    [
        ("total_precip", "Total Precipitation"),
        ("max_least_high", "Max Least High"),
        ("min_greatest_low", "Min Greatest Low"),
    ]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot displays the top ten events for a given
    site and period of your choice. Here is a description of the labels
    shown in the 'Which Metric to Summarize' option:
    <ul>
     <li><i>Total Precipitation</i>: Total precipitation over the specified
     number of days.</li>
     <li><i>Max Least High</i>: The highest minimum high temperature over
     the specified duration of days.</li>
    <li><i>Min Greatest Low</i>: The coldest maximum low temperature over
     the specified duration of days. Example series) -15 -12 -14 -16 would
     be -12</li>
    </ul>
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="total_precip",
            label="Which Metric to Summarize",
            options=METRICS,
        ),
        dict(
            type="int",
            name="days",
            default=1,
            label="Over how many consecutive days",
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


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]
    varname = ctx["var"]
    days = ctx["days"]

    table = "alldata_%s" % (station[:2],)

    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "octmar":
        months = [10, 11, 12, 1, 2, 3]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    sorder = "ASC" if varname in ["min_greatest_low"] else "DESC"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""WITH data as (
            SELECT month, day, day - ':days days'::interval as start_date,
            count(*) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as count,
            sum(precip) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as total_precip,
            min(high) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as max_least_high,
            max(low) OVER (ORDER by day ASC ROWS BETWEEN :days preceding and
            current row) as min_greatest_low
            from {table} WHERE station = :station)

            SELECT day as end_date, start_date, {varname} from data WHERE
            month in :months and
            extract(month from start_date) in :months and count = :d2 and
            {varname} is not null
            ORDER by {varname} {sorder} LIMIT 10
            """
            ),
            conn,
            params={
                "days": days - 1,
                "station": station,
                "months": tuple(months),
                "d2": days,
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("Error, no results returned!")
    ylabels = []
    fmt = "%.2f" if varname in ["total_precip"] else "%.0f"
    for _, row in df.iterrows():
        # no strftime support for old days, so we hack at it
        lbl = fmt % (row[varname],)
        if days > 1:
            sts = row["end_date"] - datetime.timedelta(days=(days - 1))
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

    fig = figure(apctx=ctx)
    ax = fig.add_axes([0.1, 0.1, 0.5, 0.8])
    ax.barh(
        range(10, 0, -1),
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
    ax.set_xlabel(
        (
            "Precipitation [inch]"
            if varname in ["total_precip"]
            else r"Temperature $^\circ$F"
        )
    )
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(
        ("%s [%s] Top 10 Events\n%s [days=%s] (%s) (%s-%s)")
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            METRICS[varname],
            days,
            MDICT[month],
            ab.year,
            datetime.datetime.now().year,
        ),
        size=12,
    )

    return fig, df


if __name__ == "__main__":
    plotter({})
