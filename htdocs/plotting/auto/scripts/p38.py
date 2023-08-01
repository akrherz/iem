"""
This plot presents daily estimates of solar radiation for a given year
for the 'climodat' stations tracked by the IEM.  These
stations only report temperature, precipitation, and snowfall, but many
users are interested in solar radiation data as well.  So estimates
are pulled from various reanalysis and forecast model analyses to generate
the numbers presented.  There are four sources of solar radiation made
available for this plot.  The HRRR data is the only one in 'real-time',
the MERRAv2/NARR lag by about a month, and the ERA5 Land lags by 8-9 days.
"""
import calendar
import datetime
import itertools

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "best": "Use ERA5 Land, then HRRR",
    "era5land_srad": "ERA5 Land (1951-)",
    "hrrr_srad": "HRRR (2013-)",
    "merra_srad": "MERRA v2 (1980-)",
    "narr_srad": "NARR (1979-)",
}
PDICT2 = {
    "era5land_srad": "ERA5 Land (1951-)",
    "hrrr_srad": "HRRR (2013-)",
    "merra_srad": "MERRA v2 (1980-)",
    "narr_srad": "NARR (1979-)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            options=PDICT,
            default="best",
            name="var",
            label="Select Radiation Source for Timeseries",
        ),
        {
            "type": "select",
            "options": PDICT2,
            "default": "era5land_srad",
            "name": "climo",
            "label": "Select Radiation Source for Climatology",
        },
        {
            "type": "year",
            "name": "year",
            "default": datetime.date.today().year,
            "min": 1951,
            "label": "Select Year to Plot:",
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    year = ctx["year"]
    varname = ctx["var"]
    climo = ctx["climo"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
            WITH agg as (
                SELECT sday,
                max({climo}),
                min({climo}),
                avg({climo})
                from alldata where
                station = %s and {climo} is not null
                GROUP by sday),
            obs as (
                SELECT sday, day, era5land_srad, narr_srad, merra_srad,
                hrrr_srad
                from alldata WHERE station = %s and year = %s)
            SELECT a.sday, a.max as max_{climo}, a.min as min_{climo},
            a.avg as avg_{climo}, o.day, o.narr_srad, o.merra_srad,
            o.hrrr_srad, o.era5land_srad
            from agg a LEFT JOIN obs o on (a.sday = o.sday)
            ORDER by a.sday ASC
        """,
            conn,
            params=(station, station, year),
            index_col="sday",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    for col in ["max", "min", "avg"]:
        df[f"{col}_{climo}_smooth"] = (
            df[f"{col}_{climo}"]
            .rolling(window=7, min_periods=1, center=True)
            .mean()
        )
    df["best"] = df["era5land_srad"].fillna(df["hrrr_srad"])
    # hack for leap day here
    if df["best"].loc["0229"] is None:
        df = df.drop("0229")

    title = (
        f"{ctx['_sname']}:: {year} Daily Solar Radiation\n"
        f"{PDICT2[climo]} Climatology"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.add_axes([0.07, 0.1, 0.45, 0.8])

    xaxis = np.arange(1, len(df.index) + 1)
    ax.fill_between(
        xaxis,
        df[f"min_{climo}"],
        df[f"max_{climo}"],
        color="tan",
        label=f"{climo.split('_')[0]} Range",
    )
    ax.plot(
        xaxis,
        df[f"avg_{climo}_smooth"],
        color="k",
        label=f"{climo.split('_')[0]} Average",
    )
    if not np.isnan(df[varname].max()):
        ax.scatter(
            xaxis,
            df[varname],
            color="g",
            label=f"{year} {varname.split('_')[0]}",
        )
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Shortwave Solar Radiation $MJ$ $d^{-1}$")
    ax.set_xlabel("* Climatology has 7 day smooth applied")

    # Do the x,y scatter plots
    opts = ["narr_srad", "merra_srad", "era5land_srad", "hrrr_srad"]
    for i, combo in enumerate(itertools.combinations(opts, 2)):
        row = i % 3
        col = i // 3
        ax3 = fig.add_axes([0.6 + (0.22 * col), 0.1 + (0.3 * row), 0.15, 0.19])
        df2 = df[df[combo[0]].notna() & df[combo[1]].notna()]

        xmax = df2[combo[0]].max()
        xlabel = combo[0].replace("_srad", "").upper()
        ylabel = combo[1].replace("_srad", "").upper()
        ymax = df2[combo[1]].max()
        if np.isnan(xmax) or np.isnan(ymax):
            ax3.text(
                0.5,
                0.5,
                f"{xlabel} or {ylabel}\nis missing",
                ha="center",
                va="center",
            )
            ax3.get_xaxis().set_visible(False)
            ax3.get_yaxis().set_visible(False)
            continue
        c = df2[[combo[0], combo[1]]].corr()
        ax3.text(
            0.5,
            1.01,
            f"Pearson Corr: {c.iat[1, 0]:.2f}",
            fontsize=10,
            ha="center",
            transform=ax3.transAxes,
        )
        ax3.scatter(
            df2[combo[0]], df2[combo[1]], edgecolor="None", facecolor="green"
        )
        maxv = max([ax3.get_ylim()[1], ax3.get_xlim()[1]])
        ax3.set_ylim(0, maxv)
        ax3.set_xlim(0, maxv)
        ax3.plot([0, maxv], [0, maxv], color="k")
        ax3.set_xlabel(
            f"{xlabel} " r"$\mu$=" f"{df2[combo[0]].mean():.1f}",
            labelpad=0,
            fontsize=12,
        )
        ax3.set_ylabel(
            f"{ylabel} " r"$\mu$=" f"{df2[combo[1]].mean():.1f}",
            fontsize=12,
        )

    return fig, df


if __name__ == "__main__":
    plotter({})
