"""One month being warmer than the other"""
import datetime
import calendar

import psycopg2.extras
import numpy as np
import pandas as pd
import matplotlib.patheffects as PathEffects
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot summarizes the frequency of one month
    being warmer than another month for that calendar year."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            label="Select Station:",
            network="IACLIMATE",
        )
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    table = "alldata_%s" % (station[:2],)

    cursor.execute(
        f"""
        SELECT year, month, avg((high+low)/2.) from {table}
        WHERE station = %s and day < %s and year > 1892
        GROUP by year, month ORDER by year ASC
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

    (fig, ax) = plt.subplots(1, 1, sharex=True, figsize=(8, 6))
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
    ax.set_title(
        ("[%s] %s\nYears that Month was Warmer than other Month")
        % (station, ctx["_nt"].sts[station]["name"])
    )
    fig.colorbar(res)
    ax.set_xlabel("This Month was Warmer than...")
    ax.set_ylabel("...this month for same year")

    return fig, df


if __name__ == "__main__":
    plotter(dict())
