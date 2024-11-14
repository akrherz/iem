"""
This plot summarizes the frequency of one month
being warmer/wetter than another month for that calendar year.
"""

import calendar
from datetime import date, datetime

import matplotlib.patheffects as PathEffects
import numpy as np
import pandas as pd
from pyiem.database import get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

from iemweb.autoplot import ARG_STATION

PDICT = {
    "high": "High Temperature Warmer",
    "low": "Low Temperature Warmer",
    "avg": "Average Temperature Warmer",
    "precip": "Total Precipitation Wetter",
}
COLSQL = {
    "high": "avg(high)",
    "low": "avg(low)",
    "avg": "avg((high+low)/2.)",
    "precip": "sum(precip)",
}
PDICT2 = {
    "no": "Don't include current month",
    "yes": "Include current month",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        {
            "type": "select",
            "name": "var",
            "default": "avg",
            "options": PDICT,
            "label": "Which Variable to Compare",
        },
        {
            "type": "select",
            "name": "inc",
            "default": "no",
            "options": PDICT2,
            "label": "Include Current Month?",
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    varname = ctx["var"]
    last_date = date.today().replace(day=1)
    if ctx["inc"] == "yes":
        last_date = date.today()

    cursor.execute(
        f"""
        SELECT year, month, {COLSQL[varname]} from alldata WHERE
        station = %s and day < %s GROUP by year, month ORDER by year ASC
        """,
        (station, last_date),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No results found for query")

    baseyear = None
    for row in cursor:
        if baseyear is None:
            baseyear = row[0]
            avgs = np.ones((datetime.now().year - baseyear + 1, 12)) * -99.0
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
            lastyear[i, j] = datetime.now().year - np.argmax(t[::-1])
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

    subtitle = f"{ctx['_sname']} [{baseyear}-]"
    title = f"Years that Month with {PDICT[varname]} than other Month"
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
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

    ax.set_xticks(range(12))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_yticks(range(12))
    ax.set_yticklabels(calendar.month_abbr[1:])
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.5, 11.5)
    fig.colorbar(res)
    ax.set_xlabel(
        f"This Month was {'Warmer' if varname != 'precip' else 'Wetter'} "
        "than..."
    )
    ax.set_ylabel("...this month for same year")

    return fig, df
