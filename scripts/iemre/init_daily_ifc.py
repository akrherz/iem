"""Generate the storage netcdf file for Iowa Flood Center Precip"""

import os
import sys
from datetime import datetime

import click
import numpy as np
from pyiem.grid.nav import IFC
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts: datetime, ci: bool):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = f"/mesonet/data/iemre/{ts.year}_ifc_daily.nc"
    if os.path.isfile(fp):
        LOG.info("Cowardly refusing to overwrite file %s.", fp)
        sys.exit()
    nc = ncopen(fp, "w")
    nc.title = f"IFC Daily Precipitation {ts:%Y}"
    nc.platform = "Grided Estimates"
    nc.description = "Iowa Flood Center ~0.004 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", 1057)
    nc.createDimension("lon", 1741)
    days = 2 if ci else ((ts.replace(year=ts.year + 1)) - ts).days
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
    lat[:] = IFC.y_points

    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "nv"))
    lat_bnds[:, 0] = IFC.y_edges[:-1]
    lat_bnds[:, 1] = IFC.y_edges[1:]

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = IFC.x_points

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "nv"))
    lon_bnds[:, 0] = IFC.x_edges[:-1]
    lon_bnds[:, 1] = IFC.x_edges[1:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {ts:%Y}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "p01d", float, ("time", "lat", "lon"), fill_value=1.0e20
    )
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()


@click.command()
@click.option("--year", required=True, type=int, help="Year to initialize")
@click.option("--ci", is_flag=True, help="Run in CI Mode")
def main(year: int, ci: bool) -> None:
    """Go Main Go"""
    init_year(datetime(year, 1, 1), ci)
    if ci:
        with ncopen(f"/mesonet/data/iemre/{year}_ifc_daily.nc", "a") as nc:
            nc.variables["p01d"][0, :, :] = 0
            nc.variables["p01d"][1, :, :] = 0


if __name__ == "__main__":
    main()
