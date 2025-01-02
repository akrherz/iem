"""Generate the yearly PRISM file to hold our data"""

import os
import sys
from datetime import datetime

import click
import numpy as np
from pyiem.grid.nav import PRISM
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts: datetime):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fn = f"/mesonet/data/prism/{ts:%Y}_daily.nc"
    if os.path.isfile(fn):
        LOG.info("Cowardly refusing to overwrite file %s.", fn)
        sys.exit()
    nc = ncopen(fn, "w")
    nc.title = f"PRISM Daily Data for {ts:%Y}"
    nc.platform = "Grided Observations"
    nc.description = "PRISM Data on a 0.04 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", PRISM.ny)
    nc.createDimension("lon", PRISM.nx)
    days = ((ts.replace(year=ts.year + 1)) - ts).days
    nc.createDimension("time", int(days))
    nc.createDimension("bnds", 2)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat.bounds = "lat_bnds"
    # We want to store the center of the grid cell
    lat[:] = PRISM.y_points

    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "bnds"))
    lat_bnds[:, 0] = PRISM.y_edges[:-1]
    lat_bnds[:, 1] = PRISM.y_edges[1:]

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon.bounds = "lon_bnds"
    lon[:] = PRISM.x_points

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "bnds"))
    lon_bnds[:, 0] = PRISM.x_edges[:-1]
    lon_bnds[:, 1] = PRISM.x_edges[1:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {ts:%Y}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    # Tracked variables
    high = nc.createVariable(
        "tmax", float, ("time", "lat", "lon"), fill_value=-9999.0
    )
    high.units = "C"
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable(
        "tmin", float, ("time", "lat", "lon"), fill_value=-9999.0
    )
    low.units = "C"
    low.long_name = "2m Air Temperature Daily High"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    p01d = nc.createVariable(
        "ppt", float, ("time", "lat", "lon"), fill_value=-9999.0
    )
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()


@click.command()
@click.option("--year", type=int, required=True, help="Year to initialize")
def main(year):
    """Run for the year."""
    os.makedirs("/mesonet/data/prism", exist_ok=True)
    init_year(datetime(year, 1, 1))


if __name__ == "__main__":
    main()
