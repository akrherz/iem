"""Generate the IEMRE climatology file, hmmm"""

import os
from datetime import datetime

import geopandas as gpd
import numpy as np
from pyiem import iemre
from pyiem.database import get_dbconn
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    fn = iemre.get_dailyc_ncname()
    if os.path.isfile(fn):
        LOG.warning("Cowardly refusing to create file: %s", fn)
        return
    nc = ncopen(fn, "w")
    nc.title = "IEM Daily Reanalysis Climatology %s" % (ts.year,)
    nc.platform = "Grided Climatology"
    nc.description = "IEM daily analysis on a 0.125 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"  # *cough*
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", iemre.NY)
    nc.createDimension("lon", iemre.NX)
    nc.createDimension("nv", 2)
    ts2 = datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension("time", int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat.bounds = "lat_bnds"
    # These are the grid centers
    lat[:] = np.arange(
        iemre.DOMAINS[""]["south"],
        iemre.DOMAINS[""]["north"] + 0.001,
        iemre.DY,
    )
    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "nv"))
    lat_bnds[:, 0] = lat[:] - iemre.DY / 2.0
    lat_bnds[:, 1] = lat[:] + iemre.DY / 2.0

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon.bounds = "lon_bnds"
    # These are the grid centers
    lon[:] = np.arange(
        iemre.DOMAINS[""]["west"],
        iemre.DOMAINS[""]["east"] + 0.001,
        iemre.DX,
    )

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "nv"))
    lon_bnds[:, 0] = lon[:] - iemre.DX / 2.0
    lon_bnds[:, 1] = lon[:] + iemre.DX / 2.0

    tm = nc.createVariable("time", float, ("time",))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    # Tracked variables
    hasdata = nc.createVariable("hasdata", np.int8, ("lat", "lon"))
    hasdata.units = "1"
    hasdata.long_name = "Analysis Available for Grid Cell"
    hasdata.coordinates = "lon lat"
    hasdata[:] = 0

    high = nc.createVariable(
        "high_tmpk", float, ("time", "lat", "lon"), fill_value=1.0e20
    )
    high.units = "K"
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable(
        "low_tmpk", float, ("time", "lat", "lon"), fill_value=1.0e20
    )
    low.units = "K"
    low.long_name = "2m Air Temperature Daily Low"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    p01d = nc.createVariable(
        "p01d", float, ("time", "lat", "lon"), fill_value=1.0e20
    )
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()


def compute_hasdata(nc):
    """Compute the has_data grid"""
    czs = CachingZonalStats(iemre.AFFINE)
    pgconn = get_dbconn("postgis")
    states = gpd.GeoDataFrame.from_postgis(
        "SELECT the_geom, state_abbr from states",
        pgconn,
        index_col="state_abbr",
        geom_col="the_geom",
    )
    data = np.flipud(nc.variables["hasdata"][:, :])
    czs.gen_stats(data, states["the_geom"])
    for nav in czs.gridnav:
        if nav is None:
            continue
        grid = np.ones((nav.ysz, nav.xsz))
        grid[nav.mask] = 0.0
        yslice = slice(nav.y0, nav.y0 + nav.ysz)
        xslice = slice(nav.x0, nav.x0 + nav.xsz)
        data[yslice, xslice] = np.where(grid > 0, 1, data[yslice, xslice])
    nc.variables["hasdata"][:, :] = np.flipud(data)


def main():
    """Go Main"""
    init_year(datetime(2000, 1, 1))
    with ncopen(iemre.get_dailyc_ncname(domain=""), "a", timeout=300) as nc:
        compute_hasdata(nc)


if __name__ == "__main__":
    main()
