"""
This application plots out the distribution of
some monthly metric for single month for all tracked sites within one
state.  The plot presents the distribution and normalized frequency
for a specific year and for all years combined for the given month.  The side
panel presents some basic statistics with the <strong>P</strong> values
representing the given percentile.
"""

import calendar
from datetime import date

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.table import table
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from scipy.stats import norm

PDICT = {
    "sum-precip": "Total Precipitation [inch]",
    "avg-high": "Average Daily High [°F]",
    "avg-low": "Average Daily Low [°F]",
    "avg-t": "Average Daily Temp [°F]",
    "avg-era5land_srad": "Average Daily Solar Radiation (ERA5Land) [MJ m-2]",
    "avg-era5land_soilt4_avg": (
        "Average Daily ~4 inch Soil Temperature (ERA5Land) [°F]"
    ),
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = date.today()
    desc["arguments"] = [
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Year to highlight:",
        ),
        {
            "type": "year",
            "name": "syear",
            "label": "Inclusive start year (if data exists) to use in plot",
            "min": 1850,
            "default": 1850,
        },
        {
            "type": "year",
            "name": "eyear",
            "label": "Inclusive end year (if data exists) to use in plot",
            "min": 1850,
            "default": today.year,
        },
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


def add_percentile_table(
    ax: Axes, alldata: pd.Series, thisyear: pd.Series, year: int
):
    """Print a table of the percentiles for this year and climatology."""
    ptiles = [0.01, 0.05, 0.2, 0.25, 0.4, 0.5, 0.6, 0.75, 0.8, 0.95, 0.99]
    allstats = alldata.describe(percentiles=ptiles)
    yearstats = thisyear.describe(percentiles=ptiles)
    cell_text = [
        [
            "Min",
            f"{allstats['min']:.2f}",
            f"{yearstats['min']:.2f}",
        ]
    ]
    for p in ptiles:
        idx = f"{int(p * 100)}%"
        cell_text.append(
            [
                f"P{int(p * 100)}",
                f"{allstats[idx]:.2f}",
                f"{yearstats[idx]:.2f}",
            ]
        )
    cell_text.append(
        [
            "Max",
            f"{allstats['max']:.2f}",
            f"{yearstats['max']:.2f}",
        ]
    )
    table(
        ax,
        cellText=cell_text,
        edges="horizontal",
        colLabels=["Stat", "All years", f"{year}"],
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    ax.axis("off")


def plotter(ctx: dict) -> tuple:
    """Go"""
    state = ctx["state"]
    year = ctx["year"]
    month = ctx["month"]
    plotvar: str = ctx["type"]

    with get_sqlalchemy_conn("coop") as conn:
        # Generate dataframe of yearly observed values for the given month
        # Exclude spatial averages other than statewide
        monthlyobs = pd.read_sql(
            sql_helper(
                """
            SELECT station, year,
            sum(precip) as "sum-precip",
            avg(high) as "avg-high",
            avg(low) as "avg-low",
            avg(era5land_srad) as "avg-era5land_srad",
            avg(era5land_soilt4_avg) as "avg-era5land_soilt4_avg",
            avg((high+low)/2.) as "avg-t",
            count(*) as obs
            from {table}
            WHERE month = :month and
            substr(station, 3, 1) not in ('C', 'D') and
            year >= :syear and year <= :eyear
            GROUP by station, year
        """,
                table=f"alldata_{state.lower()}",
            ),
            conn,
            params={
                "month": month,
                "syear": ctx["syear"],
                "eyear": ctx["eyear"],
            },
            index_col=None,
        )
        # Remove missing data
        monthlyobs = monthlyobs[monthlyobs[plotvar].notna()]
    if monthlyobs.empty:
        raise NoDataFound("No Data Found")
    stateavg = None
    if f"{state}0000" in monthlyobs["station"].values:
        stateavg = monthlyobs.loc[
            monthlyobs["station"] == f"{state}0000", plotvar
        ].mean()

    num_stations = len(monthlyobs["station"].unique())
    thisyeardf = monthlyobs[monthlyobs["year"] == year]
    title = (
        f"{reference.state_names[state]} {year} {calendar.month_name[month]} "
        f"{PDICT[plotvar]} Distribution"
    )
    subtitle = (
        "Stations with some data between "
        f"{monthlyobs['year'].min()}-{monthlyobs['year'].max()}: "
        f"{num_stations}. Stations with {year} data: {len(thisyeardf)}"
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes((0.1, 0.1, 0.5, 0.8))
    tableax = fig.add_axes((0.65, 0.3, 0.28, 0.5))
    if not thisyeardf.empty:
        _, bins, _ = ax.hist(
            thisyeardf[plotvar].to_numpy(),
            20,
            fc="lightblue",
            ec="lightblue",
            density=1,
        )
        mean = thisyeardf[plotvar].mean()
        std = monthlyobs[plotvar].std()
        y = norm.pdf(bins, mean, std)
        ax.plot(
            bins,
            y,
            "b--",
            lw=2,
            label=(
                f"{year} Normal Dist. "
                r"$\sigma$="
                f"{std:.2f} "
                r"$\mu$="
                f"{mean:.2f}"
            ),
        )

    climo_mean = monthlyobs[plotvar].mean()
    climo_std = monthlyobs[plotvar].std()
    bins = np.linspace(
        climo_mean - (climo_std * 3.0), climo_mean + (climo_std * 3.0), 30
    )
    y = norm.pdf(bins, climo_mean, climo_std)
    ax.plot(
        bins,
        y,
        "g--",
        lw=2,
        label=(
            r"Climo Normal Dist. $\sigma$="
            f"{climo_std:.2f} "
            r"$\mu$="
            f"{climo_mean:.2f}"
        ),
    )

    if stateavg is not None:
        filtered = monthlyobs[
            (monthlyobs["station"] == f"{state}0000")
            & (monthlyobs["year"] == year)
        ]
        if not filtered.empty:
            ax.axvline(
                filtered[plotvar].values[0],
                label=f"{year} State Avg {filtered[plotvar].values[0]:.2f}",
                color="r",
                lw=2,
            )
        ax.axvline(
            stateavg,
            label=f"Climo Statewide Avg {stateavg:.2f}",
            color="g",
            lw=2,
        )
    ax.set_xlabel(PDICT[plotvar])
    ax.set_ylabel("Normalized Frequency")
    ax.grid(True)
    box = ax.get_position()
    ax.set_position([box.x0, 0.26, box.width, 0.65])
    ax.legend(ncol=2, fontsize=12, loc=(-0.05, -0.35))
    if plotvar == "sum-precip":
        ax.set_xlim(left=0)

    add_percentile_table(
        tableax,
        monthlyobs[plotvar],
        thisyeardf[plotvar],
        year,
    )

    return fig, monthlyobs
