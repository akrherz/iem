"""
This plot summarizes the frequency of one month
being warmer than another month for that calendar year.
"""
import calendar
import datetime

import matplotlib.patheffects as PathEffects
import numpy as np
import pandas as pd
import psycopg2.extras
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        )
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    cursor.execute(
        """
        SELECT year, month, avg((high+low)/2.) from alldata WHERE
        station = %s and day < %s GROUP by year, month ORDER by year ASC
        """,
        (station, datetime.date.today().replace(day=1)),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No results found for query")

    for rownum, row in enumerate(cursor):
        if rownum == 0:
            baseyear = row[0]
            avgs = (
                np.ones((datetime.datetime.now().year - baseyear + 1, 12))
                * -99.0
            )
        avgs[row[0] - baseyear, row[1] - 1] = row[2]

    matrix = np.zeros((12, 12))
    lastyear = np.zeros((12, 12))
    rows = []
    for i in range(12):
        for j in range(12):
            # How many years was i warmer than j
            t = np.where(
                np.logical_and(
                    avgs[:, j] > -99,
                    np.logical_and(avgs[:, i] > avgs[:, j], avgs[:, i] > -99),
                ),
                1,
                0,
            )
            matrix[i, j] = np.sum(t)
            lastyear[i, j] = datetime.datetime.now().year - np.argmax(t[::-1])
            lyear = lastyear[i, j] if matrix[i, j] > 0 else None
            rows.append(
                dict(
                    month1=(i + 1),
                    month2=(j + 1),
                    years=matrix[i, j],
                    lastyear=lyear,
                )
            )
    df = pd.DataFrame(rows)

    title = f"{ctx['_sname']}\n" "Years that Month was Warmer than other Month"
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    x, y = np.meshgrid(np.arange(-0.5, 12.5, 1), np.arange(-0.5, 12.5, 1))
    res = ax.pcolormesh(x, y, np.transpose(matrix))
    for i in range(12):
        for j in range(12):
            txt = ax.text(
                i,
                j,
                "%s" % ("%.0f" % (matrix[i, j],) if i != j else "-"),
                va="center",
                ha="center",
                color="white",
            )
            txt.set_path_effects(
                [PathEffects.withStroke(linewidth=2, foreground="k")]
            )
            if matrix[i, j] > 0 and matrix[i, j] < 10:
                txt = ax.text(
                    i,
                    j - 0.5,
                    "%.0f" % (lastyear[i, j],),
                    fontsize=9,
                    va="bottom",
                    ha="center",
                    color="white",
                )
                txt.set_path_effects(
                    [PathEffects.withStroke(linewidth=2, foreground="k")]
                )

    ax.set_xticks(range(0, 12))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_yticks(range(0, 12))
    ax.set_yticklabels(calendar.month_abbr[1:])
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.5, 11.5)
    fig.colorbar(res)
    ax.set_xlabel("This Month was Warmer than...")
    ax.set_ylabel("...this month for same year")

    return fig, df


if __name__ == "__main__":
    plotter({})
