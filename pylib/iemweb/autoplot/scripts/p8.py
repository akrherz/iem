"""
This plot presents the frequency of having
a month's preciptation at or above some threshold.  This threshold
is compared against the long term climatology for the site and month. This
plot is designed to answer the question about reliability of monthly
precipitation for a period of your choice.
"""

import calendar
from datetime import date

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_STATION


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    y2 = date.today().year
    y1 = y2 - 20
    desc["arguments"] = [
        ARG_STATION,
        dict(type="year", name="syear", default=y1, label="Enter Start Year:"),
        dict(
            type="year",
            name="eyear",
            default=y2,
            label="Enter End Year (inclusive):",
        ),
        dict(
            type="int",
            name="threshold",
            default="80",
            label="Threshold Percentage [%]:",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    syear = ctx["syear"]
    eyear = ctx["eyear"]
    threshold = ctx["threshold"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
    with months as (
      select year, month, p, avg(p) OVER (PARTITION by month) from (
        select year, month, sum(precip) as p from alldata
        where station = :station and year < extract(year from now())
        GROUP by year, month) as foo)

    SELECT month, sum(case when p > (avg * :thres / 100.0) then 1 else 0 end)
        as hits, count(*) as total
    from months WHERE year >= :sy and year < :ey
    GROUP by month ORDER by month ASC
    """
            ),
            conn,
            params={
                "station": station,
                "thres": threshold,
                "sy": syear,
                "ey": eyear,
            },
            index_col="month",
        )
    if df.empty:
        raise NoDataFound("Failed to find any data.")
    df["freq"] = df["hits"] / df["total"] * 100.0

    title = (
        f"{ctx['_sname']} :: Monthly Precipitation Reliability\n"
        f"Period: {syear}-{eyear}, % of Months above {threshold}% "
        "of Long Term Avg"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    ax.bar(df.index.values, df["freq"].values, align="center")
    for month, row in df.iterrows():
        ax.text(
            month,
            row["freq"] + 2,
            f"{row['freq']:.1f}%",
            bbox={"color": "white"},
            ha="center",
        )
    ax.set_xticks(np.arange(1, 13))
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylabel(f"Percentage of Months, n={df['total'].max():.0f} years")
    return fig, df
