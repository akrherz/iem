"""
Simple plot of seasonal/yearly precipitation totals.
"""

import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from scipy import stats

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.barchart import barchar_with_top10

PDICT2 = {
    "winter": "Winter (Dec, Jan, Feb)",
    "fma": "FMA (Feb, Mar, Apr)",
    "spring": "Spring (Mar, Apr, May)",
    "amj": "AMJ (Apr, May, Jun)",
    "summer": "Summer (Jun, Jul, Aug)",
    "fall": "Fall (Sep, Oct, Nov)",
    "all": "Entire Year",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
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
      sum(case when month in (4, 5, 6)
      then precip else 0 end) as amj,
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
        if row[season] is not None:
            rows.append(dict(year=int(row["yr"]), value=float(row[season])))
    cursor.close()
    pgconn.close()
    df = pd.DataFrame(rows).set_index("year")

    title = (
        f"{ctx['_sname']} {df.index[0]:.0f}-{df.index[-1]:.0f} :: "
        f"Precipitation [{PDICT2[season]}] "
    )
    fig = figure(title=title, apctx=ctx)
    avgv = df["value"].mean()

    colorabove = "seagreen"
    colorbelow = "lightsalmon"
    df["color"] = np.where(df["value"] < avgv, colorbelow, colorabove)
    ax = barchar_with_top10(
        fig, df, "value", color=df["color"].to_list(), labelformat="%.2f"
    )
    ax.axhline(avgv, lw=2, color="k", zorder=2, label="Average")
    h_slope, intercept, r_value, _, _ = stats.linregress(
        df.index.values, df["value"].values
    )
    ax.plot(
        df.index.values,
        h_slope * df.index.values + intercept,
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
    ax.set_xlim(df.index[0] - 1, df.index[-1] + 1)
    ax.set_ylim(0, df["value"].max() + df["value"].max() / 10.0)
    ax.set_ylabel("Precipitation [inches]")
    ax.grid(True)
    ax.legend(ncol=2, fontsize=10)

    return fig, df.drop(columns="color")
