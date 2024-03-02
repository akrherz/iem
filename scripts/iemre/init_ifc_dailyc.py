"""Generate the IFC climatology file."""

import datetime
import os

import numpy as np
from pyiem.util import logger, ncopen

LOG = logger()
BASEDIR = "/mesonet/data/iemre"


def init_year(ts):
    """Create a new NetCDF file for a year of our specification!"""
    fn = "%s/ifc_dailyc.nc" % (BASEDIR,)
    if os.path.isfile(fn):
        LOG.info("Cowardly refusing to overwrite %s", fn)
        return
    nc = ncopen(fn, "w")
    nc.title = "IFC Climatology %s" % (ts.year,)
    nc.platform = "Grided Climatology"
    nc.description = "IFC"
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
    nc.createDimension("lat", 1057)
    nc.createDimension("lon", 1741)
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension("time", int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    # Grid centers
    lat[:] = 40.133331 + np.arange(1057) * 0.004167

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = -97.154167 + np.arange(1741) * 0.004167

    tm = nc.createVariable("time", float, ("time",))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "p01d", float, ("time", "lon", "lat"), fill_value=1.0e20
    )
    p01d.units = "mm"
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
