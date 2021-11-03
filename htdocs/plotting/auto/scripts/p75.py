"""Totals"""
import datetime

import psycopg2.extras
import numpy as np
from scipy import stats
import pandas as pd
from pyiem import network
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT2 = dict(
    [
        ("winter", "Winter (Dec, Jan, Feb)"),
        ("fma", "FMA (Feb, Mar, Apr)"),
        ("spring", "Spring (Mar, Apr, May)"),
        ("summer", "Summer (Jun, Jul, Aug)"),
        ("fall", "Fall (Sep, Oct, Nov)"),
        ("all", "Entire Year"),
    ]
)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """
    Simple plot of seasonal/yearly precipitation totals.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="season",
            default="winter",
            label="Select Season:",
            options=PDICT2,
        ),
        dict(
            type="year", name="year", default=1893, label="Start Year of Plot"
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    ccursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    season = ctx["season"]
    _ = PDICT2[season]
    startyear = ctx["year"]

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute(
        f"""
      SELECT extract(year from day + '%s month'::interval) as yr,
      sum(case when month in (12, 1, 2)
      then precip else 0 end) as winter,
      sum(case when month in (2, 3, 4)
      then precip else 0 end) as fma,
      sum(case when month in (3, 4, 5)
      then precip else 0 end) as spring,
      sum(case when month in (6, 7, 8)
      then precip else 0 end) as summer,
      sum(case when month in (9, 10, 11)
      then precip else 0 end) as fall,
      sum(precip) as all
      from {table} WHERE station = %s GROUP by yr ORDER by yr ASC
    """,
        (1 if season != "all" else 0, station),
    )
    if ccursor.rowcount == 0:
        raise NoDataFound("No Data Found.")

    today = datetime.datetime.now()
    thisyear = today.year
    if season == "spring" and today.month > 5:
        thisyear += 1
    rows = []
    for row in ccursor:
        if row["yr"] < startyear:
            continue
        rows.append(dict(year=int(row["yr"]), data=float(row[season])))
    df = pd.DataFrame(rows)

    data = np.array(df["data"])
    years = np.array(df["year"])
    title = ("[%s] %s %.0f-%.0f Precipitation [%s] ") % (
        station,
        nt.sts[station]["name"],
        min(years),
        max(years),
        PDICT2[season],
    )
    (fig, ax) = figure_axes(title=title)
    avgv = np.average(data)

    colorabove = "seagreen"
    colorbelow = "lightsalmon"
    bars = ax.bar(years, data, fc=colorabove, ec=colorabove, align="center")
    for i, mybar in enumerate(bars):
        if data[i] < avgv:
            mybar.set_facecolor(colorbelow)
            mybar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color="k", zorder=2, label="Average")
    h_slope, intercept, r_value, _, _ = stats.linregress(years, data)
    ax.plot(
        years,
        h_slope * np.array(years) + intercept,
        "--",
        lw=2,
        color="k",
        label="Trend",
    )
    ax.text(
        0.01,
        0.99,
        "Avg: %.2f, slope: %.2f inch/century, R$^2$=%.2f"
        % (avgv, h_slope * 100.0, r_value ** 2),
        transform=ax.transAxes,
        va="top",
        bbox=dict(color="white"),
    )
    ax.set_xlabel("Year")
    ax.set_xlim(min(years) - 1, max(years) + 1)
    ax.set_ylim(0, max(data) + max(data) / 10.0)
    ax.set_ylabel("Precipitation [inches]")
    ax.grid(True)
    ax.legend(ncol=2, fontsize=10)

    return fig, df


if __name__ == "__main__":
    plotter({})
