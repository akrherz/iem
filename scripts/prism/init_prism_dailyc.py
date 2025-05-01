"""Grid out dailyc for a daily climatology on PRISM grid.

Note: PRISM's climatology is monthly/annual, so no daily :/
"""

import os
from datetime import datetime

import numpy as np
from pyiem.grid.nav import PRISM800
from pyiem.util import logger, ncopen

LOG = logger()
BASEDIR = "/mesonet/data/prism"


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fn = f"{BASEDIR}/prism_dailyc.nc"
    if os.path.exists(fn):
        LOG.info("%s exists, skipping", fn)
        return
    nc = ncopen(fn, "w")
    nc.title = f"PRISM Climatology {ts.year}"
    nc.platform = "Grided Climatology"
    nc.description = "PRISM"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"  # *cough*
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", PRISM800.ny)
    nc.createDimension("lon", PRISM800.nx)
    ts2 = datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension("time", int(days))
    nc.createDimension("bnds", 2)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.bounds = "lat_bnds"
    lat.axis = "Y"
    # Grid centers
    lat[:] = PRISM800.y_points

    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "bnds"))
    lat_bnds[:, 0] = PRISM800.y_edges[:-1]
    lat_bnds[:, 1] = PRISM800.y_edges[1:]

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = PRISM800.x_points

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "bnds"))
    lon_bnds[:, 0] = PRISM800.x_edges[:-1]
    lon_bnds[:, 1] = PRISM800.x_edges[1:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {ts.year}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "ppt", np.ushort, ("time", "lat", "lon"), fill_value=65535
    )
    p01d.scale_factor = 0.01
    p01d.add_offset = 0.0
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    high = nc.createVariable(
        "tmax", np.uint8, ("time", "lat", "lon"), fill_value=255
    )
    high.scale_factor = 0.5
    high.add_offset = -60.0
    high.units = "C"
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable(
        "tmin", np.uint8, ("time", "lat", "lon"), fill_value=255
    )
    low.scale_factor = 0.5
    low.add_offset = -60.0
    low.units = "C"
    low.long_name = "2m Air Temperature Daily High"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    nc.close()


def main():
    """Go Main"""
    init_year(datetime(2000, 1, 1))


if __name__ == "__main__":
    main()
