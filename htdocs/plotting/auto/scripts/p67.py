"""
This plot displays the frequency of having a
reported wind speed be above a given threshold by reported temperature
and by month.
"""
import calendar
import datetime

import matplotlib.patheffects as PathEffects
import pandas as pd
import psycopg2.extras
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="int",
            name="threshold",
            default=10,
            label="Wind Speed Threshold (knots)",
        ),
        dict(type="month", name="month", default="3", label="Select Month:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    threshold = ctx["threshold"]
    month = ctx["month"]

    cursor.execute(
        """
        WITH data as (
            SELECT tmpf::int as t, sknt from alldata where station = %s
            and extract(month from valid) = %s and tmpf is not null
            and sknt >= 0
        )

        SELECT t, sum(case when sknt >= %s then 1 else 0 end), count(*)
        from data GROUP by t ORDER by t ASC
    """,
        (station, month, threshold),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data was Found.")
    tmpf = []
    events = []
    total = []
    hits = 0
    cnt = 0
    for row in cursor:
        if row[2] < 3:
            continue
        tmpf.append(row[0])
        hits += row[1]
        cnt += row[2]
        events.append(row[1])
        total.append(row[2])

    df = pd.DataFrame(
        dict(
            tmpf=pd.Series(tmpf),
            events=pd.Series(events),
            total=pd.Series(total),
        )
    )

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = (
        f"{ctx['_sname']}\n"
        f"Frequency of {threshold}+ knot Wind Speeds by Temperature "
        f"for {calendar.month_name[month]} "
        f"({ab.year}-{datetime.datetime.now().year})\n"
        "(must have 3+ hourly observations at the given temperature)"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.bar(
        tmpf,
        df["events"] / df["total"] * 100.0,
        width=1.1,
        ec="green",
        fc="green",
    )
    avgval = hits / float(cnt) * 100.0
    ax.axhline(avgval, lw=2, zorder=2)
    txt = ax.text(
        tmpf[10],
        avgval + 1,
        f"Average: {avgval:.1f}%",
        va="bottom",
        zorder=2,
        color="yellow",
        fontsize=14,
    )
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="k")])
    ax.grid(zorder=11)
    ax.set_ylabel("Frequency [%]")
    ax.set_ylim(0, 100)
    ax.set_xlim(min(tmpf) - 3, max(tmpf) + 3)
    ax.set_xlabel(r"Air Temperature $^\circ$F")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])

    return fig, df


if __name__ == "__main__":
    plotter({})
