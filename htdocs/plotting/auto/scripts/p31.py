"""jumps in temperature"""
import datetime
import calendar

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot displays the maximum and minimum change
    in high temperature between a given day and a given number of days prior
    to that date.  The red bars are the largest difference between a maximum
    high over a period of days and the given day.  The blue bars are the
    opposite."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="int",
            name="days",
            default="4",
            label="Number of Trailing Days:",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]

    table = "alldata_%s" % (station[:2],)

    cursor.execute(
        """
    WITH data as (
     select day, high,
     max(high) OVER
         (ORDER by day ASC rows between %s PRECEDING and 1 PRECEDING) as up,
     min(high) OVER
         (ORDER by day ASC rows between %s PRECEDING and 1 PRECEDING) as down
     from """
        + table
        + """ where station = %s
    )
    SELECT extract(week from day) as wk,
    max(high - up), min(high - down) from data
    GROUP by wk ORDER by wk ASC
    """,
        (days, days, station),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")

    weeks = []
    jump_up = []
    jump_down = []
    rows = []
    for row in cursor:
        rows.append(
            dict(week=int((row[0] - 1)), jump_up=row[1], jump_down=row[2])
        )
        weeks.append(row[0] - 1)
        jump_up.append(row[1])
        jump_down.append(row[2])
    df = pd.DataFrame(rows)
    weeks = np.array(weeks)

    extreme = max([max(jump_up), 0 - min(jump_down)]) + 10

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    (fig, ax) = plt.subplots(1, 1, sharex=True, figsize=(8, 6))
    ax.bar(weeks * 7, jump_up, width=7, fc="r", ec="r")
    ax.bar(weeks * 7, jump_down, width=7, fc="b", ec="b")
    ax.grid(True)
    ax.set_ylabel(r"Temperature Change $^\circ$F")
    ax.set_title(
        ("%s %s\nMax Change in High Temp by Week of Year")
        % (station, ctx["_nt"].sts[station]["name"])
    )
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)
    ax.set_ylim(0 - extreme, extreme)
    ax.text(
        183,
        extreme - 5,
        ("Maximum Jump in High Temp vs Max High over past %s days") % (days,),
        color="red",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )
    ax.text(
        183,
        0 - extreme + 5,
        ("Maximum Dip in High Temp vs Min High over past %s days") % (days,),
        color="blue",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict())
