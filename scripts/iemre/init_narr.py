"""Generate the storage of NARR 3 hourly products"""

import os
import sys
from datetime import datetime

import click
import numpy as np
import pygrib
from pyiem.util import archive_fetch, logger, ncopen

# This exists on dev laptop :/
TEMPLATE_FN = "1980/01/01/model/NARR/apcp_198001010000.grib"
BASEDIR = "/mesonet/data/iemre"
LOG = logger()


@click.command()
@click.option("--year", type=int, required=True)
def main(year: int):
    """
    Create a new NetCDF file for a year of our specification!
    """
    ts = datetime(year, 1, 1)
    # Load up the example grib file to base our file on
    with archive_fetch(TEMPLATE_FN) as fn:
        grbs = pygrib.open(fn)
        grb = grbs[1]
        # grid shape is y, x
        lats, lons = grb.latlons()

    fp = f"{BASEDIR}/{ts.year}_narr.nc"
    if os.path.isfile(fp):
        LOG.info("Cowardly refusing to overwrite file %s.", fp)
        sys.exit()
    nc = ncopen(fp, "w")
    nc.title = f"IEM Packaged NARR for {ts.year}"
    nc.platform = "Grided Reanalysis"
    nc.description = "NARR Data"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("x", lats.shape[1])
    nc.createDimension("y", lats.shape[0])
    nc.createDimension("bnds", 2)
    ts2 = datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    print(f"Year {ts.year} has {days} days")
    nc.createDimension("time", int(days) * 8)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("y", "x"))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = lats

    lon = nc.createVariable("lon", float, ("y", "x"))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = lons

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Hours since {ts.year}-01-01 00:00:0.0"
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
    main()
