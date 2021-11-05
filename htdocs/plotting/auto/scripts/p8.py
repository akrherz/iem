""" Monthly precip reliability"""
import calendar
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem import network
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    y2 = datetime.date.today().year
    y1 = y2 - 20
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(type="year", name="syear", default=y1, label="Enter Start Year:"),
        dict(
            type="year",
            name="eyear",
            default=y2,
            label="Enter End Year (inclusive):",
        ),
        dict(
            type="int",
            name="threshold",
            default="80",
            label="Threshold Percentage [%]:",
        ),
    ]
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents the frequency of having
    a month's preciptation at or above some threshold.  This threshold
    is compared against the long term climatology for the site and month. This
    plot is designed to answer the question about reliability of monthly
    precipitation for a period of your choice. """
    return desc


def plotter(fdict):
    """Go"""
    coop = get_dbconn("coop")
    cursor = coop.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    syear = ctx["syear"]
    eyear = ctx["eyear"]
    threshold = ctx["threshold"]

    nt = network.Table("%sCLIMATE" % (station[:2],))

    cursor.execute(
        f"""
    with months as (
      select year, month, p, avg(p) OVER (PARTITION by month) from (
        select year, month, sum(precip) as p from alldata_{station[:2]}
        where station = %s and year < extract(year from now())
        GROUP by year, month) as foo)

    SELECT month, sum(case when p > (avg * %s / 100.0) then 1 else 0 end)
    from months WHERE year >= %s and year < %s
    GROUP by month ORDER by month ASC
    """,
        (station, threshold, syear, eyear),
    )
    vals = []
    years = float(1 + eyear - syear)
    for row in cursor:
        vals.append(row[1] / years * 100.0)
    if not vals:
        raise NoDataFound("No Data Found!")
    df = pd.DataFrame(
        dict(freq=pd.Series(vals, index=range(1, 13))),
        index=pd.Series(range(1, 13), name="month"),
    )

    title = (
        "%s [%s] Monthly Precipitation Reliability\n"
        "Period: %s-%s, %% of Months above %s%% of Long Term Avg"
    ) % (nt.sts[station]["name"], station, syear, eyear, threshold)
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    ax.bar(np.arange(1, 13), vals, align="center")
    ax.set_xticks(np.arange(1, 13))
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylabel("Percentage of Months, n=%.0f years" % (years,))
    return fig, df


if __name__ == "__main__":
    plotter({})
