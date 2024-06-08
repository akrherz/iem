"""
This application will make a map with the number
of days it takes to accumulate a given amount of precipitation.  This is
based on progressing daily back in time for up to 90 days to accumulate
the specified amount.  This plot will take some time to generate, so please
be patient with it!
"""

import datetime
import os

import geopandas as gpd
import numpy as np
from pyiem import iemre, util
from pyiem.exceptions import NoDataFound
from pyiem.grid.zs import CachingZonalStats
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": False}
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(type="state", name="sector", default="IA", label="Select State:"),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="Date:",
            min="2011/01/01",
        ),
        dict(
            type="float",
            name="threshold",
            default=2.0,
            label="Date Precipitation Threshold (inch)",
        ),
        dict(type="cmap", name="cmap", default="terrain", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = util.get_autoplot_context(fdict, get_description())
    date = ctx["date"]
    sector = ctx["sector"]
    threshold = ctx["threshold"]
    threshold_mm = util.convert_value(threshold, "inch", "millimeter")

    idx1 = iemre.daily_offset(date)
    ncfn = iemre.get_daily_mrms_ncname(date.year)
    if not os.path.isfile(ncfn):
        raise NoDataFound("No data found.")
    ncvar = "p01d"

    # Get the state weight
    with util.get_sqlalchemy_conn("postgis") as conn:
        df = gpd.GeoDataFrame.from_postgis(
            "SELECT the_geom from states where state_abbr = %s",
            conn,
            params=(sector,),
            index_col=None,
            geom_col="the_geom",
        )
    czs = CachingZonalStats(iemre.MRMS_AFFINE)
    steps = 0
    with util.ncopen(ncfn) as nc:
        czs.gen_stats(
            np.zeros((nc.variables["lat"].size, nc.variables["lon"].size)),
            df["the_geom"],
        )
        jslice = None
        islice = None
        for nav in czs.gridnav:
            # careful here as y is flipped in this context
            jslice = slice(
                nc.variables["lat"].size - (nav.y0 + nav.ysz),
                nc.variables["lat"].size - nav.y0,
            )
            islice = slice(nav.x0, nav.x0 + nav.xsz)

        grid = np.zeros(
            (jslice.stop - jslice.start, islice.stop - islice.start)
        )
        total = np.zeros(
            (jslice.stop - jslice.start, islice.stop - islice.start)
        )
        lon = nc.variables["lon"][islice]
        lat = nc.variables["lat"][jslice]

        for idx in range(idx1, max(-1, idx1 - 91), -1):
            total += nc.variables[ncvar][idx, jslice, islice]
            grid = np.where(
                np.logical_and(grid == 0, total > threshold_mm), steps, grid
            )
            steps += 1
    # Do we need to do a previous year?
    if steps < 90:
        ncfn = iemre.get_daily_mrms_ncname(date.year - 1)
        if not os.path.isfile(ncfn):
            raise NoDataFound("No data found.")
        with util.ncopen(ncfn) as nc:
            idx1 = iemre.daily_offset(datetime.date(date.year - 1, 12, 31))
            while steps < 91:
                total += nc.variables[ncvar][idx, jslice, islice]
                grid = np.where(
                    np.logical_and(grid == 0, total > threshold_mm),
                    steps,
                    grid,
                )
                idx1 -= 1
                steps += 1

    mp = MapPlot(
        apctx=ctx,
        sector="state",
        state=sector,
        titlefontsize=14,
        subtitlefontsize=12,
        title=(
            "NOAA MRMS: Number of Recent Days "
            f'till Accumulating {threshold}" of Precip'
        ),
        subtitle=(
            f"valid {date:%-d %b %Y}: based on per calendar day "
            "estimated preciptation, MultiSensorPass2 and "
            "RadarOnly products"
        ),
        nocaption=True,
    )
    x, y = np.meshgrid(lon, lat)
    cmap = get_cmap(ctx["cmap"])
    cmap.set_over("k")
    cmap.set_under("white")
    mp.pcolormesh(
        x, y, grid, np.arange(0, 91, 15), cmap=cmap, units="days", extend="max"
    )
    mp.drawcounties()
    mp.drawcities()

    return mp.fig


if __name__ == "__main__":
    plotter({})
