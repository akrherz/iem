"""Generate the storage of NARR 3 hourly products"""
from __future__ import print_function
import datetime
import sys

import numpy as np
import pygrib
from pyiem.util import ncopen

# This exists on dev laptop :/
TEMPLATE_FN = (
    "/mesonet/ARCHIVE/data/1980/01/01/model/" "NARR/apcp_198001010000.grib"
)
BASEDIR = "/mesonet/data/iemre"


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    # Load up the example grib file to base our file on
    grbs = pygrib.open(TEMPLATE_FN)
    grb = grbs[1]
    # grid shape is y, x
    lats, lons = grb.latlons()

    fp = "%s/%s_narr.nc" % (BASEDIR, ts.year)
    nc = ncopen(fp, "w")
    nc.title = "IEM Packaged NARR for %s" % (ts.year,)
    nc.platform = "Grided Reanalysis"
    nc.description = "NARR Data"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = ("%s Generated") % (
        datetime.datetime.now().strftime("%d %B %Y"),
    )
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("x", lats.shape[1])
    nc.createDimension("y", lats.shape[0])
    nc.createDimension("bnds", 2)
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    print("Year %s has %s days" % (ts.year, days))
    nc.createDimension("time", int(days) * 8)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", np.float, ("y", "x"))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = lats

    lon = nc.createVariable("lon", np.float, ("y", "x"))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = lons

    tm = nc.createVariable("time", np.float, ("time",))
    tm.units = "Hours since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm.bounds = "time_bnds"
    tm[:] = np.arange(0, int(days) * 8) * 3

    tmb = nc.createVariable("time_bnds", "d", ("time", "bnds"))
    tmb[:, 0] = np.arange(0, int(days) * 8) * 3 - 1
    tmb[:, 1] = np.arange(0, int(days) * 8) * 3

    # 3 hour accum, 0 to 655.35
    apcp = nc.createVariable(
        "apcp", np.ushort, ("time", "y", "x"), fill_value=65535
    )
    apcp.scale_factor = 0.01
    apcp.add_offset = 0.0
    apcp.units = "mm"
    apcp.long_name = "Precipitation"
    apcp.standard_name = "Precipitation"
    apcp.coordinates = "lon lat"
    apcp.description = "Precipitation accumulation for the previous 3 hours"

    nc.close()


if __name__ == "__main__":
    init_year(datetime.datetime(int(sys.argv[1]), 1, 1))
