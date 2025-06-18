"""
Using the gridded IEM ReAnalysis of daily
precipitation.  This chart presents the areal coverage of some trailing
number of days precipitation for a state of your choice.  This application
does not properly account for the trailing period of precipitation during
the first few days of January.  This application only works for contiguous
states.
"""

import os
from datetime import date, timedelta

import geopandas as gpd
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.grid import nav
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import daily_offset, get_daily_ncname
from pyiem.plot import figure_axes
from pyiem.util import ncopen


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = date.today()
    desc["arguments"] = [
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Select Year",
            min=1893,
        ),
        dict(
            type="float",
            name="threshold",
            default="1.0",
            label="Precipitation Threshold [inch]",
        ),
        dict(
            type="int", name="period", default="7", label="Over Period of Days"
        ),
        {
            "type": "state",
            "name": "state",
            "default": "IA",
            "label": "For Contiguous US State Only:",
            "contiguous": True,
        },
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    year = ctx["year"]
    threshold = ctx["threshold"]
    period = ctx["period"]
    state = ctx["state"]

    with get_sqlalchemy_conn("postgis") as conn:
        states = gpd.read_postgis(
            sql_helper(
                "SELECT the_geom, state_abbr from states "
                "where state_abbr = :abbr"
            ),
            conn,
            params={"abbr": state},
            index_col="state_abbr",
            geom_col="the_geom",
        )  # type: ignore

    ncfn = get_daily_ncname(year)
    if not os.path.isfile(ncfn):
        raise NoDataFound("Data not available for year")
    with ncopen(ncfn) as nc:
        precip = nc.variables["p01d"]
        czs = CachingZonalStats(nav.IEMRE.affine_image)
        hasdata = np.zeros(
            (nc.dimensions["lat"].size, nc.dimensions["lon"].size)
        )
        czs.gen_stats(hasdata, states["the_geom"])
        for gnav in czs.gridnav:
            if gnav is None:
                continue
            grid = np.ones((gnav.ysz, gnav.xsz))
            grid[gnav.mask] = 0.0
            jslice = slice(gnav.y0, gnav.y0 + gnav.ysz)
            islice = slice(gnav.x0, gnav.x0 + gnav.xsz)
            hasdata[jslice, islice] = np.where(
                grid > 0, 1, hasdata[jslice, islice]
            )
        hasdata = np.flipud(hasdata)
        datapts = np.sum(np.where(hasdata > 0, 1, 0))
        if datapts == 0:
            raise NoDataFound("Application does not work for non-CONUS.")

        now = date(year, 1, 1)
        now += timedelta(days=period - 1)
        ets = min(date.today(), date(year, 12, 31))
        days = []
        coverage = []
        while now <= ets:
            idx = daily_offset(now)
            sevenday = np.sum(precip[(idx - period) : idx, :, :], 0)
            pday = np.where(hasdata > 0, sevenday[:, :], -1)
            tots = np.sum(np.where(pday >= (threshold * 25.4), 1, 0))
            days.append(now)
            coverage.append(tots / float(datapts) * 100.0)

            now += timedelta(days=1)
    df = pd.DataFrame(
        {"day": pd.Series(days), "coverage": pd.Series(coverage)}
    )

    title = (
        f"{year} IEM Estimated Areal "
        f"Coverage Percentage of {reference.state_names[state]}"
    )
    subtitle = (
        f"Receiving {threshold:.2f} inches of precip over "
        f"trailing {period} day period from {days[0]} to {days[-1]}"
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    ax.bar(days, coverage, fc="g", ec="g", align="center")
    ax.set_xlim(days[0] - timedelta(days=1), days[-1] + timedelta(days=1))
    ax.set_ylabel("Areal Coverage [%]")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%-d"))
    ax.set_yticks(range(0, 101, 25))
    ax.grid(True)
    return fig, df
