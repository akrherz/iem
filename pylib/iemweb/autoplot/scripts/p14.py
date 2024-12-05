"""
Using long term data, five precipitation bins are
constructed such that each bin contributes 20% to the annual precipitation
total.  Using these 5 bins, an individual year's worth of data is
compared.  With this comparison, you can say that one's years worth of
departures can be explained by these differences in precipitation bins.
"""

from datetime import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

from iemweb.autoplot import ARG_STATION


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="year",
            name="year",
            default=datetime.now().year,
            label="Year to Highlight:",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn, cursor = get_dbconnc("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    today = datetime.now()
    year = ctx["year"]
    jdaylimit = 367
    if year == today.year:
        jdaylimit = int(today.strftime("%j"))

    endyear = int(datetime.now().year) + 1

    cursor.execute(
        """
        select precip, sum(precip) OVER (ORDER by precip ASC) as rsum,
        sum(precip) OVER () as tsum,
        min(year) OVER () as minyear from alldata where
        station = %s and precip > 0.009 and extract(doy from day) < %s and
        year < extract(year from now()) ORDER by precip ASC
    """,
        (station, jdaylimit),
    )
    if cursor.rowcount == 0:
        pgconn.close()
        raise NoDataFound("No Data Found.")
    total = None
    base = None
    bins = [0.01]
    minyear = None
    row = None
    for i, row in enumerate(cursor):
        if i == 0:
            minyear = row["minyear"]
            total = row["tsum"]
            onefifth = total / 5.0
            base = onefifth
        if row["rsum"] > base:
            bins.append(row["precip"])
            base += onefifth

    normal = total / float(endyear - minyear - 1)
    # A rounding edge case
    if row["precip"] != bins[-1]:
        bins.append(row["precip"])

    df = pd.DataFrame(
        {"bin": range(1, 6), "lower": bins[0:-1], "upper": bins[1:]},
        index=range(1, 6),
    )

    yearlybins = np.zeros((endyear - minyear, 5), "f")
    yearlytotals = np.zeros((endyear - minyear, 5), "f")

    cursor.execute(
        """
    SELECT year,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin0,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin1,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin2,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin3,
    sum(case when precip >= %s and precip < %s then 1 else 0 end) as bin4,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot0,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot1,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot2,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot3,
    sum(case when precip >= %s and precip < %s then precip else 0 end) as tot4
    from alldata where extract(doy from day) < %s and
    station = %s and precip > 0 and year > 1879 GROUP by year
    """,
        (
            bins[0],
            bins[1],
            bins[1],
            bins[2],
            bins[2],
            bins[3],
            bins[3],
            bins[4],
            bins[4],
            bins[5],
            bins[0],
            bins[1],
            bins[1],
            bins[2],
            bins[2],
            bins[3],
            bins[3],
            bins[4],
            bins[4],
            bins[5],
            jdaylimit,
            station,
        ),
    )
    for row in cursor:
        for i in range(5):
            yearlybins[int(row["year"]) - minyear, i] = row[f"bin{i}"]
            yearlytotals[int(row["year"]) - minyear, i] = row[f"tot{i}"]
    pgconn.close()
    avgs = np.average(yearlybins, 0)
    df["avg_days"] = avgs
    dlast = yearlybins[year - minyear, :]
    df[f"days_{year}"] = dlast
    df[f"precip_{year}"] = yearlytotals[year - minyear, :]
    df[f"normal_{year}"] = normal / 5.0

    ybuffer = (max([max(avgs), max(dlast)]) + 2) * 0.05
    addl = ""
    if jdaylimit < 367:
        addl = f" thru {today:%-d %b}"
    title = (
        f"{ctx['_sname']} [{minyear}-{endyear - 1}]\n"
        f"Daily Precipitation Contributions{addl}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    bars = ax.bar(
        np.arange(5) - 0.2,
        avgs,
        width=0.4,
        fc="b",
        align="center",
        label=f'Average = {normal:.2f}"',
    )
    for i, _bar in enumerate(bars):
        ax.text(
            _bar.get_x() + 0.2,
            avgs[i] + ybuffer,
            f"{avgs[i]:.1f}",
            ha="center",
            zorder=2,
        )
        delta = yearlytotals[year - minyear, i] / normal * 100.0 - 20.0
        ax.text(
            i,
            max(avgs[i], dlast[i]) + 2 * ybuffer,
            f"{'+' if delta > 0 else ''}{delta:.1f}%",
            ha="center",
            color="r",
            bbox=dict(pad=0, facecolor="white", edgecolor="white"),
            fontsize="larger",
        )

    bars = ax.bar(
        np.arange(5) + 0.2,
        dlast,
        width=0.4,
        fc="r",
        align="center",
        label=f'{year} = {np.sum(yearlytotals[year - minyear, :]):.2f}"',
    )
    for i, _bar in enumerate(bars):
        ax.text(
            _bar.get_x() + 0.2,
            dlast[i] + ybuffer,
            f"{dlast[i]:.0f}",
            ha="center",
            fontsize="larger",
        )

    ax.text(
        0.7,
        0.8,
        f"Red text represents {year} bin total\nprecip departure from average",
        transform=ax.transAxes,
        color="r",
        ha="center",
        va="top",
        bbox={"facecolor": "white", "edgecolor": "white"},
    )
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Days")
    ax.text(
        0.5,
        -0.05,
        "Precipitation Bins [inch], split into equal 20%"
        f" by rain volume ({(normal / 5.):.2f}in) over period of record",
        transform=ax.transAxes,
        va="top",
        ha="center",
    )
    ax.set_xticks(np.arange(0, 5))
    xlabels = [f"{bins[i]:.2f}-{bins[i + 1]:.2f}" for i in range(5)]
    ax.set_xticklabels(xlabels)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.1)

    return fig, df
