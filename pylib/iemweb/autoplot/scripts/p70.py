"""
This chart attempts to display the period between the first and last VTEC
enabled watch, warning or advisory <strong>issuance</strong> by year.  For
some long term products, like Flood Warnings, this plot does not attempt
to show the time domain that those products were valid, only the issuance.
The right two plots display the total number of events and the total
number of dates with at least one event.</p>

<p>The left plot can be colorized by either coloring the event counts per
day or the accumulated "year/season to date" total.</p>

<p>For the purposes of this plot, an event is defined by a single VTEC
event identifier usage.  For example, a single Tornado Watch covering
10 counties only counts as one event. The simple average is computed
over the years excluding the first and last year.</p>

<p>When you split this plot by 1 July, the year shown is for the year of
the second half of this period, ie 2020 is 1 Jul 2019 - 30 Jun 2020.</p>
"""

from datetime import date, timedelta

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from matplotlib.colorbar import ColorbarBase
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure, get_cmap
from pyiem.plot.use_agg import plt
from pyiem.reference import state_names

from iemweb.autoplot import ARG_FEMA, FEMA_REGIONS, fema_region2states

PDICT = {"jan1": "January 1", "jul1": "July 1"}
PDICT2 = {
    "wfo": "View by Single NWS Forecast Office",
    "state": "View by State",
    "fema": "View by FEMA Region",
}
PDICT3 = {
    "daily": "Color bars with daily issuance totals",
    "accum": "Color bars with accumulated year to date totals",
    "none": "Bars should not be colored, please",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            default="wfo",
            options=PDICT2,
            label="View by WFO or State?",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(type="state", default="IA", name="state", label="Select State:"),
        ARG_FEMA,
        dict(
            type="phenomena",
            name="phenomena",
            default="SV",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
        ),
        dict(
            type="select",
            options=PDICT,
            label="Split the year on date:",
            default="jan1",
            name="split",
        ),
        dict(
            type="select",
            options=PDICT3,
            label="How to color bars for left plot:",
            default="daily",
            name="f",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"][:4]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    split = ctx["split"]
    opt = ctx["opt"]
    state = ctx["state"]

    params = {
        "phenomena": phenomena,
        "significance": significance,
        "state": state,
        "station": station,
    }
    wfolimiter = " wfo = :station "
    if opt == "state":
        wfolimiter = " substr(ugc, 1, 2) = :state "
    elif opt == "fema":
        wfolimiter = " substr(ugc, 1, 2) = ANY(:states) "
        params["states"] = fema_region2states(ctx["fema"])
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper(
                """WITH data as (
                SELECT eventid, wfo, vtec_year,
                min(date(issue)) as date from warnings where {wfolimiter}
                and phenomena = :phenomena and significance = :significance
                GROUP by eventid, wfo, vtec_year)
            SELECT vtec_year, date, count(*) from data GROUP by vtec_year, date
            ORDER by vtec_year ASC, date ASC
            """,
                wfolimiter=wfolimiter,
            ),
            conn,
            params=params,
            index_col=None,
            parse_dates=[
                "date",
            ],
        )
    if df.empty:
        raise NoDataFound("No data found for query")

    # We have an edge case of vtec_year != date.year, remove those rows
    df = df[df["vtec_year"] == df["date"].dt.year]

    # Since many VTEC events start in 2005, we should not trust any
    # data that has its first year in 2005
    if df["vtec_year"].min() == 2005 and split == "jan1":
        df = df[df["vtec_year"] > 2005]
    # Split the season at jul 1, if requested
    if split == "jul1":
        df["vtec_year"] = df.apply(
            lambda x: x["vtec_year"] + 1
            if x["date"].month > 6
            else x["vtec_year"],
            axis=1,
        )
        df["doy"] = df.apply(
            lambda x: x["date"] - pd.Timestamp(x["vtec_year"] - 1, 7, 1),
            axis=1,
        )
    else:
        df["doy"] = df.apply(
            lambda x: x["date"] - pd.Timestamp(x["vtec_year"], 1, 1), axis=1
        )
    df["doy"] = df["doy"].dt.days

    title = f"[{station}] NWS {ctx['_nt'].sts[station]['name']}"
    if opt == "state":
        title = f"NWS Issued Alerts for State of {state_names[state]}"
    elif opt == "fema":
        title = f"NWS Issued Alerts for FEMA {FEMA_REGIONS[ctx['fema']]}"
    title += (
        "\n"
        "Period between First and Last "
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance})"
    )

    fig = figure(apctx=ctx, title=title)
    ax = fig.add_axes((0.12, 0.1, 0.61, 0.8))

    # Create a color bar for the number of events per day
    cmap = get_cmap(ctx["cmap"])
    cmap.set_under("tan")
    cmap.set_over("black")
    bins = [1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 50]
    if ctx["f"] == "accum":
        maxval = (
            int(
                df[["vtec_year", "count"]]
                .groupby("vtec_year")
                .sum()
                .max()
                .iloc[0]
            )
            + 1
        )
        if maxval < 11:
            bins = np.arange(1, 11)
        elif maxval < 21:
            bins = np.arange(1, 21)
        else:
            bins = np.linspace(1, maxval, 20, dtype="i")

    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    if ctx["f"] != "none":
        cax = fig.add_axes(
            [0.01, 0.12, 0.02, 0.6], frameon=False, yticks=[], xticks=[]
        )
        cb = ColorbarBase(
            cax, norm=norm, cmap=cmap, extend="max", spacing="proportional"
        )
        cb.set_label(
            "Daily Count" if ctx["f"] == "daily" else "Accum Count",
            loc="bottom",
        )

    for year, gdf in df.groupby("vtec_year"):
        size = max(gdf["doy"].max() - gdf["doy"].min(), 1)
        ax.barh(
            year,
            size,
            left=gdf["doy"].min(),
            ec="brown",
            fc="tan",
            align="center",
        )
        if ctx["f"] == "none":
            continue
        if ctx["f"] == "daily":
            ax.barh(
                gdf["vtec_year"].values,
                [1] * len(gdf.index),
                left=gdf["doy"].values,
                align="center",
                zorder=3,
                color=cmap(norm([gdf["count"]]))[0],
            )
            continue
        # Do the fancy pants accum
        gdf["cumsum"] = gdf["count"].cumsum()
        ax.barh(
            gdf["vtec_year"].values[::-1],
            gdf["doy"].values[::-1] - gdf["doy"].values[0] + 1,
            left=[gdf["doy"].values[0]] * len(gdf.index),
            zorder=3,
            align="center",
            color=cmap(norm([gdf["cumsum"].values[::-1]]))[0],
        )
    gdf = df[["vtec_year", "doy"]].groupby("vtec_year").agg(["min", "max"])
    if len(gdf.index) < 3:
        raise NoDataFound("Not enough data to compute an average")
    # Exclude first and last year in the average
    avg_start = np.average(gdf["doy", "min"].values[1:-1])
    avg_end = np.average(gdf["doy", "max"].values[1:-1])
    ax.axvline(avg_start, ls=":", lw=2, color="k")
    ax.axvline(avg_end, ls=":", lw=2, color="k")
    x0 = date(2000, 1 if split == "jan1" else 7, 1)
    _1 = (x0 + timedelta(days=int(avg_start))).strftime("%-d %b")
    _2 = (x0 + timedelta(days=int(avg_end))).strftime("%-d %b")
    ax.set_xlabel(f"Average Start Date: {_1}, End Date: {_2}")
    ax.grid()
    xticks = []
    xticklabels = []
    for i in range(367):
        dt = x0 + timedelta(days=i)
        if dt.day == 1:
            xticks.append(i)
            xticklabels.append(dt.strftime("%b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(df["doy"].min() - 10, df["doy"].max() + 10)
    ax.set_ylabel("Year")
    ax.set_ylim(df["vtec_year"].min() - 0.5, df["vtec_year"].max() + 0.5)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # ______________________________________________
    ax = fig.add_axes((0.75, 0.1, 0.1, 0.8))
    gdf = df[["vtec_year", "count"]].groupby("vtec_year").sum()
    ax.barh(
        gdf.index.values,
        gdf["count"].values,
        color="blue" if ctx["f"] != "accum" else cmap(norm([gdf["count"]]))[0],
        align="center",
    )
    ax.set_ylim(df["vtec_year"].min() - 0.5, df["vtec_year"].max() + 0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Events")
    xloc = plt.MaxNLocator(3)
    ax.xaxis.set_major_locator(xloc)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # __________________________________________
    ax = fig.add_axes((0.88, 0.1, 0.1, 0.8))
    gdf = df[["vtec_year", "count"]].groupby("vtec_year").count()
    ax.barh(gdf.index.values, gdf["count"].values, fc="blue", align="center")
    ax.set_ylim(df["vtec_year"].min() - 0.5, df["vtec_year"].max() + 0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Dates")
    xloc = plt.MaxNLocator(3)
    ax.xaxis.set_major_locator(xloc)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    return fig, df
