"""
Simple plot of seasonal/yearly precipitation totals.
"""
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconnc
from scipy import stats

PDICT2 = {
    "winter": "Winter (Dec, Jan, Feb)",
    "fma": "FMA (Feb, Mar, Apr)",
    "spring": "Spring (Mar, Apr, May)",
    "summer": "Summer (Jun, Jul, Aug)",
    "fall": "Fall (Sep, Oct, Nov)",
    "all": "Entire Year",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
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
    pgconn, cursor = get_dbconnc("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    season = ctx["season"]
    _ = PDICT2[season]
    startyear = ctx["year"]

    cursor.execute(
        """
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
      from alldata WHERE station = %s GROUP by yr ORDER by yr ASC
    """,
        (1 if season != "all" else 0, station),
    )
    if cursor.rowcount == 0:
        pgconn.close()
        raise NoDataFound("No Data Found.")

    today = datetime.datetime.now()
    thisyear = today.year
    if season == "spring" and today.month > 5:
        thisyear += 1
    rows = []
    for row in cursor:
        if row["yr"] < startyear:
            continue
        rows.append(dict(year=int(row["yr"]), data=float(row[season])))
    pgconn.close()
    df = pd.DataFrame(rows)

    data = np.array(df["data"])
    years = np.array(df["year"])
    title = (
        f"{ctx['_sname']} {min(years):.0f}-{max(years):.0f} :: "
        f"Precipitation [{PDICT2[season]}] "
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
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
        f"Avg: {avgv:.2f}, slope: {(h_slope * 100.):.2f} inch/century, "
        f"R$^2$={(r_value**2):.2f}",
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
