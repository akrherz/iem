"""
Simple plot of seasonal/yearly precipitation totals.
"""

from datetime import datetime
from typing import Annotated

import numpy as np
import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from scipy import stats

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.barchart import barchart_with_top10
from iemweb.autoplot.description import PlotDescription, SelectArg, YearArg
from iemweb.autoplot.params import AutoplotParams

PDICT2 = {
    "winter": "Winter (Dec, Jan, Feb)",
    "fma": "FMA (Feb, Mar, Apr)",
    "spring": "Spring (Mar, Apr, May)",
    "amj": "AMJ (Apr, May, Jun)",
    "summer": "Summer (Jun, Jul, Aug)",
    "fall": "Fall (Sep, Oct, Nov)",
    "all": "Entire Year",
}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    season: Annotated[
        str, SelectArg(label="Select Season:", options=PDICT2)
    ] = "winter"
    year: Annotated[int, YearArg(label="Start Year of Plot")] = 1893


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    pgconn, cursor = get_dbconnc("coop")
    station = ctx.station
    season = ctx.season
    _ = PDICT2[season]
    startyear = ctx.year

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

    today = datetime.now()
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
    if not rows:
        raise NoDataFound("No Data Found.")
    df = pd.DataFrame(rows).set_index("year")

    title = (
        f"{ctx.sname} {df.index[0]:.0f}-{df.index[-1]:.0f} :: "
        f"Precipitation [{PDICT2[season]}] "
    )
    fig = figure(title=title, apctx=ctx)
    avgv = df["value"].mean()

    colorabove = "seagreen"
    colorbelow = "lightsalmon"
    df["color"] = np.where(df["value"] < avgv, colorbelow, colorabove)
    ax = barchart_with_top10(
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
        f"Avg: {avgv:.2f}, slope: {(h_slope * 100.0):.2f} inch/century, "
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
