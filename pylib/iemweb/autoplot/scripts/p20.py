"""
This chart displays the number of hourly
observations each month that reported measurable precipitation.  Sites
are able to report trace amounts, but those reports are not considered
in hopes of making the long term climatology comparable.
"""

import calendar
from datetime import date

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    ts = date.today()
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(type="year", name="year", default=ts.year, label="Select Year:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    year = ctx["year"]

    # Oh, the pain of floating point comparison here.
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text("""
        WITH obs as (
            SELECT distinct date_trunc('hour', valid) as t from alldata
            WHERE station = :station and p01i > 0.009
        ), agg1 as (
            SELECT extract(year from t) as year, extract(month from t)
            as month, count(*) from obs GROUP by year, month
        ), averages as (
            SELECT month, avg(count), max(count) from agg1 GROUP by month
        ), myyear as (
            SELECT month, count from agg1 where year = :year
        ), ranks as (
            SELECT month, year,
            rank() OVER (PARTITION by month ORDER by count DESC)
            from agg1
        ), top as (
            SELECT month, max(year) as max_year from ranks
            WHERE rank = 1 GROUP by month
        ), agg2 as (
            SELECT t.month, t.max_year, a.avg, a.max from top t JOIN averages a
            on (t.month = a.month)
        )
        SELECT a.month, m.count as count, a.avg, a.max, a.max_year from
        agg2 a LEFT JOIN myyear m
        on (m.month = a.month) ORDER by a.month ASC
        """),
            conn,
            params={"station": station, "year": year},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Precipitation Data Found for Site")
    title = (
        f"{ctx['_sname']} :: Number of Hours with "
        "*Measurable* Precipitation Reported"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    monthly = df["avg"].values.tolist()
    bars = ax.bar(
        df["month"] - 0.2,
        monthly,
        fc="red",
        ec="red",
        width=0.4,
        label="Climatology",
        align="center",
    )
    for i, _ in enumerate(bars):
        ax.text(i + 1 - 0.25, monthly[i] + 1, f"{monthly[i]:.0f}", ha="center")
    thisyear = df["count"].values.tolist()
    if not all(a is None for a in thisyear):
        bars = ax.bar(
            np.arange(1, 13) + 0.2,
            thisyear,
            fc="blue",
            ec="blue",
            width=0.4,
            label=str(year),
            align="center",
        )
        for i, _ in enumerate(bars):
            if not np.isnan(thisyear[i]):
                ax.text(
                    i + 1 + 0.25,
                    thisyear[i] + 1,
                    f"{thisyear[i]:.0f}",
                    ha="center",
                )

    ax.scatter(
        df["month"],
        df["max"],
        marker="s",
        s=45,
        label="Max",
        zorder=2,
        color="g",
    )
    for _, row in df.iterrows():
        ax.text(
            row["month"],
            row["max"],
            f"{row['max_year']:.0f}\n{row['max']:.0f} ",
            ha="right",
        )
    ax.set_xticks(range(13))
    ax.set_xticklabels(calendar.month_abbr)
    ax.set_xlim(0, 13)
    maxval = df["count"].max()
    if not np.isnan(maxval):
        ax.set_ylim(0, max([maxval, df["max"].max()]) * 1.2)
    maxval = df["max"].max()
    if not np.isnan(maxval):
        ax.set_yticks(np.arange(0, maxval + 20, 12))
    ax.set_ylabel("Hours with 0.01+ inch precip")
    today = date.today()
    if today.year == year:
        ax.set_xlabel(f"For {year}, valid till {today:%-d %B}.")
    ax.grid(True)
    ax.legend(ncol=3)

    return fig, df
