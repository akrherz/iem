"""
This is a complex plot to describe!  For each
24 hour period (roughly ending 7 AM), the IEM computes a gridded
precipitation estimate.  This chart displays the daily coverage of a
specified intensity for that day.  The chart also compares this coverage
against the portion of the state that was below a second given threshold
over X number of days.  This provides some insight into if the
precipitation fell over locations that needed it.
"""

import os
from datetime import date, datetime, timedelta

import geopandas as gpd
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from metpy.units import units
from pyiem import iemre, reference
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.grid.zs import CachingZonalStats
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, ncopen


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = date.today()
    desc["arguments"] = [
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Select Year (1893-)",
        ),
        dict(
            type="float",
            name="daythres",
            default="0.50",
            label="1 Day Precipitation Threshold [inch]",
        ),
        dict(
            type="int",
            name="period",
            default="7",
            label="Over Period of Trailing Days",
        ),
        dict(
            type="float",
            name="trailthres",
            default="0.50",
            label="Trailing Day Precipitation Threshold [inch]",
        ),
        dict(type="state", name="state", default="IA", label="For State"),
    ]
    return desc


def do_date(ctx, now: datetime, precip, daythres, trailthres):
    """Do the local date and return a dict"""
    idx = iemre.daily_offset(now)
    ctx["days"].append(now)
    sevenday = np.sum(precip[(idx - ctx["period"]) : idx, :, :], 0)
    ptrail = np.where(ctx["iowa"] > 0, sevenday, -1)
    pday = np.where(ctx["iowa"] > 0, precip[idx, :, :], -1)
    tots = np.sum(np.where(pday >= daythres, 1, 0))
    need = np.sum(
        np.where(np.logical_and(ptrail < trailthres, ptrail >= 0), 1, 0)
    )
    htot = np.sum(
        np.where(np.logical_and(ptrail < trailthres, pday >= daythres), 1, 0)
    )
    return dict(
        day=now.strftime("%Y-%m-%d"),
        coverage=(tots / ctx["iowapts"] * 100.0),
        hits=(htot / ctx["iowapts"] * 100.0),
        efficiency=(htot / need * 100.0),
        needed=(need / ctx["iowapts"] * 100.0),
    )


def get_data(ctx):
    """Do the processing work, please"""
    with get_sqlalchemy_conn("postgis") as conn:
        states = gpd.GeoDataFrame.from_postgis(
            "SELECT the_geom, state_abbr from states where state_abbr = %s",
            conn,
            params=(ctx["state"],),
            index_col="state_abbr",
            geom_col="the_geom",
        )
    if states.empty:
        raise NoDataFound("No data was found.")

    ncfn = iemre.get_daily_ncname(ctx["year"])
    if not os.path.isfile(ncfn):
        raise NoDataFound(f"Missing {ncfn}")
    with ncopen(ncfn) as nc:
        precip = nc.variables["p01d"]
        czs = CachingZonalStats(iemre.AFFINE)
        hasdata = np.zeros(
            (nc.dimensions["lat"].size, nc.dimensions["lon"].size)
        )
        czs.gen_stats(hasdata, states["the_geom"])
        for nav in czs.gridnav:
            grid = np.ones((nav.ysz, nav.xsz))
            grid[nav.mask] = 0.0
            jslice = slice(nav.y0, nav.y0 + nav.ysz)
            islice = slice(nav.x0, nav.x0 + nav.xsz)
            hasdata[jslice, islice] = np.where(
                grid > 0, 1, hasdata[jslice, islice]
            )
        ctx["iowa"] = np.flipud(hasdata)
        ctx["iowapts"] = float(np.sum(np.where(hasdata > 0, 1, 0)))

        now = datetime(ctx["year"], 1, 1)
        now += timedelta(days=ctx["period"] - 1)
        ets = datetime(ctx["year"], 12, 31)
        today = datetime.now()
        if ets > today:
            ets = today - timedelta(days=1)
        ctx["days"] = []
        rows = []
        trailthres = (
            (ctx["trailthres"] * units("inch")).to(units("mm")).magnitude
        )
        daythres = (ctx["daythres"] * units("inch")).to(units("mm")).magnitude
        while now < ets:
            row = do_date(ctx, now, precip, daythres, trailthres)
            if row:
                rows.append(row)
            now += timedelta(days=1)

    return pd.DataFrame(rows)


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    daythres = ctx["daythres"]
    trailthres = ctx["trailthres"]
    period = ctx["period"]
    state = ctx["state"][:2]
    df = get_data(ctx)
    if df.empty:
        raise NoDataFound("No data found for query.")

    fig = figure(apctx=ctx)
    ax = fig.subplots(2, 1, sharex=True)
    ax[0].bar(
        ctx["days"],
        df["coverage"],
        fc="g",
        ec="g",
        zorder=1,
        label=f"Daily {daythres:.2f}in",
    )
    ax[0].bar(
        ctx["days"],
        df["hits"],
        fc="b",
        ec="b",
        zorder=2,
        label='Over "Dry" Areas',
    )
    ax[0].legend(loc=2, ncol=2, fontsize=10)
    ax[0].set_title(
        "IEM Estimated Areal Coverage Percent of "
        f"{reference.state_names[state]}\n"
        f" receiving daily {daythres:.2f}in vs trailing {period} "
        f"day {trailthres:.2f}in"
    )
    ax[0].set_ylabel("Areal Coverage [%]")
    ax[0].grid(True)

    ax[1].bar(ctx["days"], df["needed"], fc="tan", ec="tan", zorder=1)
    ax[1].bar(ctx["days"], df["efficiency"], fc="b", ec="b", zorder=2)
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    ax[1].grid(True)
    ax[1].set_ylabel("Areal Coverage [%]")
    ax[1].set_title(
        f"Percentage of Dry Area (tan) below ({trailthres:.2f}in "
        f"over {period} days)"
        f" got {daythres:.2f}in precip (blue) that day",
        fontsize=12,
    )
    return fig, df
