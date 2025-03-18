"""Generate the IEMRE climatology file, hmmm"""

import os
from datetime import datetime

import numpy as np
from pyiem.grid.nav import get_nav
from pyiem.iemre import DOMAINS, get_dailyc_ncname
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(domain: str, ts: datetime):
    """
    Create a new NetCDF file for a year of our specification!
    """
    gridnav = get_nav("iemre", domain)
    fn = get_dailyc_ncname(domain)
    if os.path.isfile(fn):
        LOG.warning("Cowardly refusing to create file: %s", fn)
        return
    nc = ncopen(fn, "w")
    nc.title = f"IEM Daily Reanalysis Climatology {ts:%Y}"
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
    nc.createDimension("lat", gridnav.ny)
    nc.createDimension("lon", gridnav.nx)
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
    lat[:] = gridnav.y_points
    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "nv"))
    lat_bnds[:, 0] = gridnav.y_edges[:-1]
    lat_bnds[:, 1] = gridnav.y_edges[1:]

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon.bounds = "lon_bnds"
    # These are the grid centers
    lon[:] = gridnav.x_points

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "nv"))
    lon_bnds[:, 0] = gridnav.x_edges[:-1]
    lon_bnds[:, 1] = gridnav.x_edges[1:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {ts:%Y}-01-01 00:00:0.0"
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


def main():
    """Go Main"""
    for domain in DOMAINS:
        init_year(domain, datetime(2000, 1, 1))


if __name__ == "__main__":
    main()
