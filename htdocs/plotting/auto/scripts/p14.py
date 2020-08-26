"""Precip bins"""
import datetime

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
    ] = """Using long term data, five precipitation bins are
    constructed such that each bin contributes 20% to the annual precipitation
    total.  Using these 5 bins, an individual year's worth of data is
    compared.  With this comparison, you can say that one's years worth of
    departures can be explained by these differences in precipitation bins."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="year",
            name="year",
            default=datetime.datetime.now().year,
            label="Year to Highlight:",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    today = datetime.datetime.now()
    year = ctx["year"]
    jdaylimit = 367
    if year == today.year:
        jdaylimit = int(today.strftime("%j"))

    table = "alldata_%s" % (station[:2],)
    endyear = int(datetime.datetime.now().year) + 1
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    cursor.execute(
        f"""
        select precip, sum(precip) OVER (ORDER by precip ASC) as rsum,
        sum(precip) OVER () as tsum,
        min(year) OVER () as minyear from {table} where
        station = %s and precip > 0.009 and extract(doy from day) < %s and
        year < extract(year from now()) ORDER by precip ASC
    """,
        (station, jdaylimit),
    )
    if cursor.rowcount == 0:
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
    from """
        + table
        + """ where extract(doy from day) < %s and
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
            yearlybins[int(row[0]) - minyear, i] = row["bin%s" % (i,)]
            yearlytotals[int(row[0]) - minyear, i] = row["tot%s" % (i,)]

    avgs = np.average(yearlybins, 0)
    df["avg_days"] = avgs
    dlast = yearlybins[year - minyear, :]
    df["days_%s" % (year,)] = dlast
    df["precip_%s" % (year,)] = yearlytotals[year - minyear, :]
    df["normal_%s" % (year,)] = normal / 5.0

    ybuffer = (max([max(avgs), max(dlast)]) + 2) * 0.05

    bars = ax.bar(
        np.arange(5) - 0.2,
        avgs,
        width=0.4,
        fc="b",
        align="center",
        label='Average = %.2f"' % (normal,),
    )
    for i, _bar in enumerate(bars):
        ax.text(
            _bar.get_x() + 0.2,
            avgs[i] + ybuffer,
            "%.1f" % (avgs[i],),
            ha="center",
            zorder=2,
        )
        delta = yearlytotals[year - minyear, i] / normal * 100.0 - 20.0
        ax.text(
            i,
            max(avgs[i], dlast[i]) + 2 * ybuffer,
            "%s%.1f%%" % ("+" if delta > 0 else "", delta),
            ha="center",
            color="r",
            bbox=dict(pad=0, facecolor="white", edgecolor="white"),
        )

    bars = ax.bar(
        np.arange(5) + 0.2,
        dlast,
        width=0.4,
        fc="r",
        align="center",
        label='%s = %.2f"' % (year, np.sum(yearlytotals[year - minyear, :])),
    )
    for i, _bar in enumerate(bars):
        ax.text(
            _bar.get_x() + 0.2,
            dlast[i] + ybuffer,
            "%.0f" % (dlast[i],),
            ha="center",
        )

    ax.text(
        0.7,
        0.8,
        ("Red text represents %s bin total\nprecip " "departure from average")
        % (year,),
        transform=ax.transAxes,
        color="r",
        ha="center",
        va="top",
        bbox=dict(facecolor="white", edgecolor="white"),
    )
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Days")
    ax.text(
        0.5,
        -0.05,
        (
            "Precipitation Bins [inch], split into equal 20%%"
            " by rain volume (%.2fin)"
        )
        % (normal / 5.0,),
        transform=ax.transAxes,
        va="top",
        ha="center",
    )
    addl = ""
    if jdaylimit < 367:
        addl = " thru %s" % (today.strftime("%-d %b"),)
    ax.set_title(
        ("%s [%s] [%s-%s]\nDaily Precipitation Contributions%s")
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            minyear,
            endyear - 2,
            addl,
        )
    )
    ax.set_xticks(np.arange(0, 5))
    xlabels = []
    for i in range(5):
        xlabels.append("%.2f-%.2f" % (bins[i], bins[i + 1]))
    ax.set_xticklabels(xlabels)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.1)

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="IA7708", year=2017, network="IACLIMATE"))
