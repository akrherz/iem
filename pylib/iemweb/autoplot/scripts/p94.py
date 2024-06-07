"""
This plot looks at the effect of splitting a 24
hour period at different hours of the day.  Using the hourly temperature
record, we can look at the bias of computing the daily high and low
temperature.  Confusing?  Assuming that the 'truth' is a daily high and
low computed at midnight, we can compare this value against 24 hour periods
computed for each hour of the day. This plot is one of the main reasons
that comparing climate data for a station that changed hour of day
observation over the years is problematic.
"""

import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        )
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]

    cursor.execute(
        """
    WITH obs as (select valid at time zone %s + '10 minutes'::interval as v,
    tmpf from alldata
    WHERE station = %s and tmpf >= -90 and tmpf < 150),
    s as (SELECT generate_series(0, 23, 1) || ' hours' as series),
    daily as (select s.series, v + s.series::interval as t, tmpf from obs, s),
    sums as (select series, date(t), max(tmpf), min(tmpf) from daily
    GROUP by series, date)

    SELECT series, avg(max), avg(min) from sums GROUP by series
    """,
        (ctx["_nt"].sts[station]["tzname"], station),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data found.")

    rows = []
    hrs = range(25)
    highs = [None] * 25
    lows = [None] * 25
    for row in cursor:
        i = int(row[0].split()[0])
        highs[24 - i] = row[1]
        lows[24 - i] = row[2]
        rows.append(dict(offset=(24 - i), avg_high=row[1], avg_low=row[2]))
    rows.append(dict(offset=0, avg_high=highs[24], avg_low=lows[24]))
    highs[0] = highs[24]
    lows[0] = lows[24]
    df = pd.DataFrame(rows)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = f"{ctx['_sname']} ({ab.year}-{datetime.date.today().year})"
    subtitle = "Bias of 24 Hour 'Day' Split for Average High + Low Temp"
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    ax.plot(
        hrs, np.array(highs) - highs[0], label="High Temp", lw=2, color="r"
    )
    ax.plot(hrs, np.array(lows) - lows[0], label="Low Temp", lw=2, color="b")
    ax.set_ylabel(r"Average Temperature Difference $^\circ$F")
    ax.set_xlim(0, 24)
    ax.set_xticks((0, 4, 8, 12, 16, 20, 24))
    ax.set_xticklabels(("Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM", "Mid"))
    ax.grid(True)
    ax.set_xlabel("Hour Used for 24 Hour Summary")

    ax.legend(loc="best")
    return fig, df


if __name__ == "__main__":
    plotter({})
