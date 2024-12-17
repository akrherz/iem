"""Generate the IEMRE climatology file, hmmm"""

import datetime
import os

import numpy as np
from pyiem import iemre
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    fn = iemre.get_dailyc_mrms_ncname()
    # Centroid of the upper left pixel
    ulx = -125.995
    uly = 49.995
    ny = 2700
    nx = 6100
    dx = 0.01
    dy = 0.01
    # Centroid of the lower right pixel
    lry = 23.005
    lrx = -65.005
    if os.path.isfile(fn):
        LOG.warning("Cowardly refusing to create fn: %s", fn)
        return
    nc = ncopen(fn, "w")
    nc.title = "IEM Daily Reanalysis Climatology %s" % (ts.year,)
    nc.platform = "Grided Climatology"
    nc.description = "IEM daily analysis on a 0.01 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"  # *cough*
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (
        datetime.datetime.now().strftime("%d %B %Y"),
    )
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", ny)
    nc.createDimension("lon", nx)
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension("time", int(days))
    nc.createDimension("nv", 2)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.bounds = "lat_bnds"
    lat.axis = "Y"
    # Grid centers
    lat[:] = np.arange(lry, uly + 0.0001, dy)

    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "nv"))
    lat_bnds[:, 0] = lat[:] - dy / 2.0
    lat_bnds[:, 1] = lat[:] + dy / 2.0

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = np.arange(ulx, lrx + 0.0001, dx)

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "nv"))
    lon_bnds[:, 0] = lon[:] - dx / 2.0
    lon_bnds[:, 1] = lon[:] + dx / 2.0

    tm = nc.createVariable("time", float, ("time",))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "p01d", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    p01d.units = "mm"
    p01d.scale_factor = 0.01
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()


def main():
    """Go Main"""
    init_year(datetime.datetime(2000, 1, 1))


if __name__ == "__main__":
    main()
