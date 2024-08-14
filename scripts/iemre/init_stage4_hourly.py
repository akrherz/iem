"""Generate the storage of stage IV hourly products"""

import datetime
import os

import click
import numpy as np
import pygrib
from pyiem.util import archive_fetch, logger, ncopen

BASEDIR = "/mesonet/data/stage4"
LOG = logger()


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    # Load up the example grib file to base our file on
    with archive_fetch("2014/09/09/stage4/ST4.2014090900.01h.grib") as fn:
        grbs = pygrib.open(fn)
    grb = grbs[1]
    # grid shape is y, x
    lats, lons = grb.latlons()

    os.makedirs(BASEDIR, exist_ok=True)
    fp = f"{BASEDIR}/{ts:%Y}_stage4_hourly.nc"
    if os.path.isfile(fp):
        LOG.warning("Cowardly refusing to overwrite %s", fp)
        return
    nc = ncopen(fp, "w")
    nc.title = f"IEM Packaged NOAA Stage IV for {ts:Y}"
    nc.platform = "Grided Estimates"
    nc.description = "NOAA Stage IV on HRAP Grid"
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
    LOG.info("Year %s has %s days", ts.year, days)
    nc.createDimension("time", int(days) * 24)

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
    tm.units = "Hours since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days) * 24)
    tm.bounds = "time_bnds"

    tmb = nc.createVariable("time_bnds", "d", ("time", "bnds"))
    tmb[:, 0] = np.arange(0, int(days) * 24) - 1
    tmb[:, 1] = np.arange(0, int(days) * 24)

    p01m = nc.createVariable(
        "p01m", np.ushort, ("time", "y", "x"), fill_value=65535
    )
    p01m.scale_factor = 0.01
    p01m.add_offset = 0.0
    p01m.units = "mm"
    p01m.long_name = "Precipitation"
    p01m.standard_name = "Precipitation"
    p01m.coordinates = "lon lat"
    p01m.description = "Precipitation accumulation for the previous hour"

    # Track variable status to prevent double writes of data, prior to bias
    # correction making some changes
    status = nc.createVariable(
        "p01m_status", np.int8, ("time",), fill_value=-1
    )
    status.units = "1"
    status.long_name = "p01m Variable Status"
    status.description = "-1 unset, 1 grib data copied, 2 QC Run"

    nc.close()


@click.command()
@click.option("--year", type=int, required=True, help="year")
def main(year: int):
    """Go Main!"""
    init_year(datetime.datetime(year, 1, 1))


if __name__ == "__main__":
    main()
