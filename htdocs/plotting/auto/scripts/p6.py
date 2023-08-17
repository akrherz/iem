"""
This application plots out the distribution of
some monthly metric for single month for all tracked sites within one
state.  The plot presents the distribution and normalized frequency
for a specific year and for all years combined for the given month.
"""
# pylint: disable=no-member
import calendar
import datetime

import numpy as np
import pandas as pd
from pyiem import reference
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from scipy.stats import norm

PDICT = {
    "sum-precip": "Total Precipitation [inch]",
    "avg-high": "Average Daily High [F]",
    "avg-low": "Average Daily Low [F]",
    "avg-t": "Average Daily Temp [F]",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    desc["arguments"] = [
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="year", name="year", default=today.year, label="Select Year"
        ),
        dict(
            type="month",
            name="month",
            default=today.month,
            label="Select Month",
        ),
        dict(
            type="select",
            name="type",
            default="sum-precip",
            label="Which metric to plot?",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"]
    year = ctx["year"]
    month = ctx["month"]
    ptype = ctx["type"]
    ptype_climo = ptype.split("-")[1]

    # Compute the bulk statistics for climatology
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
        WITH yearly as (
            SELECT station, year, sum(precip) as sum_precip,
            avg(high) as avg_high, avg(low) as avg_low,
            avg((high+low)/2.) as avg_temp from alldata_{state}
            WHERE month = %s GROUP by station, year)

        SELECT avg(sum_precip) as avg_precip, stddev(sum_precip) as std_precip,
        avg(avg_high) as avg_high, stddev(avg_high) as std_high,
        avg(avg_temp) as avg_t, stddev(avg_high) as std_t,
        avg(avg_low) as avg_low, stddev(avg_low) as std_low from yearly
    """,
            conn,
            params=(month,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found")
    climo_avg = df.at[0, "avg_" + ptype_climo]
    climo_std = df.at[0, "std_" + ptype_climo]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
        WITH yearly as (
            SELECT station, year, sum(precip) as sum_precip,
            avg(high) as avg_high, avg(low) as avg_low,
            avg((high+low)/2.) as avg_temp from alldata_{state}
            WHERE month = %s GROUP by station, year),
        agg1 as (
            SELECT station, avg(sum_precip) as precip,
            avg(avg_high) as high, avg(avg_low) as low,
            avg(avg_temp) as temp from yearly GROUP by station),
        thisyear as (
            SELECT station, sum_precip, avg_high, avg_low, avg_temp from yearly
            WHERE year = %s)

        SELECT a.station, a.precip as climo_precip, a.high as climo_high,
        a.low as climo_low, a.temp as climo_t,
        t.sum_precip as "sum-precip", t.avg_high as "avg-high",
        t.avg_low as "avg-low", t.avg_temp as "avg-t"
        FROM agg1 a JOIN thisyear t on (a.station = t.station)
        """,
            conn,
            params=(month, year),
            index_col="station",
        )
    if f"{state}0000" not in df.index:
        raise NoDataFound("No Data Found")
    stateavg = df.at[f"{state}0000", ptype]

    title = (
        f"{reference.state_names[state]} {year} {calendar.month_name[month]} "
        f"{PDICT[ptype]} Distribution\nNumber of stations: {len(df.index)}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    _, bins, _ = ax.hist(
        df[ptype].dropna(), 20, fc="lightblue", ec="lightblue", density=1
    )
    y = norm.pdf(bins, df[ptype].mean(), df[ptype].std())
    ax.plot(
        bins,
        y,
        "b--",
        lw=2,
        label=(
            f"{year} Normal Dist. "
            r"$\sigma$="
            f"{df[ptype].std():.2f} "
            r"$\mu$="
            f"{df[ptype].mean():.2f}"
        ),
    )

    bins = np.linspace(
        climo_avg - (climo_std * 3.0), climo_avg + (climo_std * 3.0), 30
    )
    y = norm.pdf(bins, climo_avg, climo_std)
    ax.plot(
        bins,
        y,
        "g--",
        lw=2,
        label=(
            r"Climo Normal Dist. $\sigma$="
            f"{climo_std:.2f} "
            r"$\mu$="
            f"{climo_avg:.2f}"
        ),
    )

    if stateavg is not None:
        ax.axvline(
            stateavg,
            label=f"{year} Statewide Avg {stateavg:.2f}",
            color="b",
            lw=2,
        )
    stateavg = df.at[f"{state}0000", "climo_" + ptype_climo]
    if stateavg is not None:
        ax.axvline(
            stateavg,
            label=f"Climo Statewide Avg {stateavg:.2f}",
            color="g",
            lw=2,
        )
    ax.set_xlabel(PDICT[ptype])
    ax.set_ylabel("Normalized Frequency")
    ax.grid(True)
    box = ax.get_position()
    ax.set_position([box.x0, 0.26, box.width, 0.65])
    ax.legend(ncol=2, fontsize=12, loc=(-0.05, -0.35))
    if ptype == "sum-precip":
        ax.set_xlim(left=0)

    return fig, df


if __name__ == "__main__":
    plotter({"type": "avg-low", "year": 2014, "month": 12})
