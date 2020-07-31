"""Precip days to accumulate"""
import datetime
import os

import numpy as np
import geopandas as gpd
from pyiem import iemre, util
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.grid.zs import CachingZonalStats
from pyiem.datatypes import distance
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = False
    desc[
        "description"
    ] = """This application will make a map with the number
    of days it takes to accumulate a given amount of precipitation.  This is
    based on progressing daily back in time for up to 90 days to accumulate
    the specified amount.  This plot will take some time to generate, so please
    be patient with it!
    """
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
    """ Go """
    ctx = util.get_autoplot_context(fdict, get_description())
    date = ctx["date"]
    sector = ctx["sector"]
    threshold = ctx["threshold"]
    threshold_mm = distance(threshold, "IN").value("MM")
    window_sts = date - datetime.timedelta(days=90)
    if window_sts.year != date.year:
        raise NoDataFound("Sorry, do not support multi-year plots yet!")

    # idx0 = iemre.daily_offset(window_sts)
    idx1 = iemre.daily_offset(date)
    ncfn = iemre.get_daily_mrms_ncname(date.year)
    if not os.path.isfile(ncfn):
        raise NoDataFound("No data found.")
    ncvar = "p01d"

    # Get the state weight
    df = gpd.GeoDataFrame.from_postgis(
        """
    SELECT the_geom from states where state_abbr = %s
    """,
        util.get_dbconn("postgis"),
        params=(sector,),
        index_col=None,
        geom_col="the_geom",
    )
    czs = CachingZonalStats(iemre.MRMS_AFFINE)
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
        for i, idx in enumerate(range(idx1, idx1 - 90, -1)):
            total += nc.variables[ncvar][idx, jslice, islice]
            grid = np.where(
                np.logical_and(grid == 0, total > threshold_mm), i, grid
            )
        lon = nc.variables["lon"][islice]
        lat = nc.variables["lat"][jslice]

    mp = MapPlot(
        sector="state",
        state=sector,
        titlefontsize=14,
        subtitlefontsize=12,
        title=(
            "NOAA MRMS Q3: Number of Recent Days "
            'till Accumulating %s" of Precip'
        )
        % (threshold,),
        subtitle=(
            "valid %s: based on per calendar day "
            "estimated preciptation, GaugeCorr and "
            "RadarOnly products"
        )
        % (date.strftime("%-d %b %Y"),),
    )
    x, y = np.meshgrid(lon, lat)
    cmap = get_cmap(ctx["cmap"])
    cmap.set_over("k")
    cmap.set_under("white")
    mp.pcolormesh(x, y, grid, np.arange(0, 81, 10), cmap=cmap, units="days")
    mp.drawcounties()
    mp.drawcities()

    return mp.fig


if __name__ == "__main__":
    plotter(dict())
