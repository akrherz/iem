"""Generate the storage netcdf file for 0.01deg MRMS data."""

import datetime
import os

import click
import numpy as np
from pyiem import iemre
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts, for_dep=False):
    """Create the netcdf file for a given year.

    Args:
        ts (datetime): timestamp to use for year
        for_dep (bool): are we doing this for the Daily Erosion Project?
    """

    fn = iemre.get_daily_mrms_ncname(ts.year)
    dom = iemre.DOMAINS[""]
    if for_dep:
        fn = fn.replace("daily", "dep")
    if os.path.isfile(fn):
        LOG.warning("Cowardly refusing to overwrite %s", fn)
        return
    nc = ncopen(fn, "w")
    nc.title = f"MRMS Daily Precipitation {ts.year}"
    nc.platform = "Grided Estimates"
    nc.description = "MRMS 0.01 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", (dom["north"] - dom["south"]) * 100.0)
    nc.createDimension("lon", (dom["east"] - dom["west"]) * 100.0)
    days = ((ts.replace(year=ts.year + 1)) - ts).days
    day_axis = np.arange(0, int(days))
    if for_dep:
        # April 11 through June 15
        days = 20 + 31 + 15
        tidx0 = iemre.daily_offset(ts.replace(month=4, day=11))
        day_axis = np.arange(tidx0, tidx0 + days)
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
    lat[:] = np.arange(dom["south"] + 0.005, dom["north"], 0.01)

    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "nv"))
    lat_bnds[:, 0] = np.arange(dom["south"], dom["north"], 0.01)
    lat_bnds[:, 1] = np.arange(dom["south"] + 0.01, dom["north"] + 0.01, 0.01)

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = np.arange(dom["west"], dom["east"], 0.01)

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "nv"))
    lon_bnds[:, 0] = np.arange(dom["west"], dom["east"], 0.01)
    lon_bnds[:, 1] = np.arange(dom["west"] + 0.01, dom["east"] + 0.01, 0.01)

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {ts.year}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = day_axis

    # 0 to 65535 by 0.01
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


@click.command()
@click.option("--year", type=int, help="Year to initialize")
def main(year):
    """Go Main Go."""
    init_year(datetime.datetime(year, 1, 1), False)
    init_year(datetime.datetime(year, 1, 1), True)


if __name__ == "__main__":
    main()
