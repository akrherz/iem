"""Generate the storage of stage IV hourly products"""

import os
from datetime import datetime
from typing import Optional

import click
import numpy as np
import pygrib
from pyiem import stage4
from pyiem.util import archive_fetch, logger, ncopen

BASEDIR = "/mesonet/data/stage4"
LOG = logger()


def init_year(ts: datetime, ci: bool) -> Optional[str]:
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
    fn = f"{BASEDIR}/{ts:%Y}_stage4_hourly.nc"
    if os.path.isfile(fn):
        LOG.warning("Cowardly refusing to overwrite %s", fn)
        return None
    nc = ncopen(fn, "w")
    nc.title = f"IEM Packaged NOAA Stage IV for {ts:Y}"
    nc.platform = "Grided Estimates"
    nc.description = "NOAA Stage IV on HRAP Grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = ("%s Generated") % (datetime.now().strftime("%d %B %Y"),)
    nc.comment = "No Comment at this time"
    # Store projection information
    nc.proj4 = stage4.PROJ.srs
    # Setup Dimensions
    nc.createDimension("x", lats.shape[1])
    nc.createDimension("y", lats.shape[0])
    nc.createDimension("bnds", 2)
    ts2 = datetime(ts.year + 1, 1, 1)
    days = 2 if ci else (ts2 - ts).days
    LOG.info("Year %s has %s days", ts.year, days)
    nc.createDimension("time", int(days) * 24)

    x = nc.createVariable("x", float, ("x",))
    x.units = "m"
    x.long_name = "X coordinate of projection"
    x.standard_name = "projection_x_coordinate"
    x.axis = "X"
    x.bounds = "x_bounds"
    x[:] = stage4.XAXIS

    x_bounds = nc.createVariable("x_bounds", float, ("x", "bnds"))
    x_bounds[:, 0] = stage4.XAXIS - stage4.DX / 2.0
    x_bounds[:, 1] = stage4.XAXIS + stage4.DX / 2.0

    y = nc.createVariable("y", float, ("y",))
    y.units = "m"
    y.long_name = "Y coordinate of projection"
    y.standard_name = "projection_y_coordinate"
    y.axis = "Y"
    y.bounds = "y_bounds"
    y[:] = stage4.YAXIS

    y_bounds = nc.createVariable("y_bounds", float, ("y", "bnds"))
    y_bounds[:, 0] = stage4.YAXIS - stage4.DY / 2.0
    y_bounds[:, 1] = stage4.YAXIS + stage4.DY / 2.0

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
    tm.units = f"Hours since {ts:%Y}-01-01 00:00:0.0"
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
    return fn


@click.command()
@click.option("--year", type=int, required=True, help="year")
@click.option("--ci", is_flag=True, help="Run in CI mode")
def main(year: int, ci: bool):
    """Go Main!"""
    fn = init_year(datetime(year, 1, 1), ci)
    if ci and fn is not None:
        with ncopen(fn, "a") as nc:
            nc.variables["p01m"][:] = 0
            nc.variables["p01m_status"][:] = 1


if __name__ == "__main__":
    main()
