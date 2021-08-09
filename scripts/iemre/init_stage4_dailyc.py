"""Generate the StageIV climatology file."""
import datetime
import os

import numpy as np
from pyiem.util import ncopen, logger

LOG = logger()
BASEDIR = "/mesonet/data/stage4"


def init_year(ts):
    """Create a new NetCDF file for a year of our specification!"""
    # Get existing stageIV netcdf file to copy its cordinates from
    tmplnc = ncopen(f"{BASEDIR}/2020_stage4_hourly.nc", "r")

    fn = "%s/stage4_dailyc.nc" % (BASEDIR,)
    if os.path.isfile(fn):
        LOG.info("Cowardly refusing to overwrite %s", fn)
        return
    nc = ncopen(fn, "w")
    nc.title = "StageIV Climatology %s" % (ts.year,)
    nc.platform = "Grided Climatology"
    nc.description = "StageIV"
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
    nc.createDimension("x", tmplnc.dimensions["x"].size)
    nc.createDimension("y", tmplnc.dimensions["y"].size)
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension("time", int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("y", "x"))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    # Grid centers
    lat[:] = tmplnc.variables["lat"][:]

    lon = nc.createVariable("lon", float, ("y", "x"))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = tmplnc.variables["lon"][:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "p01d_12z", float, ("time", "y", "x"), fill_value=1.0e20
    )
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()
    tmplnc.close()


def main():
    """Go Main"""
    init_year(datetime.datetime(2000, 1, 1))


if __name__ == "__main__":
    main()
