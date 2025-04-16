"""Generate the IEMRE daily analysis file for a year"""

import os
import sys
from datetime import datetime

import click
import numpy as np
from pyiem.grid.nav import get_nav
from pyiem.iemre import get_daily_ncname
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts, domain, ci: bool):
    """
    Create a new NetCDF file for a year of our specification!
    """
    gridnav = get_nav("iemre", domain)
    fn = get_daily_ncname(ts.year, domain)
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    if os.path.isfile(fn):
        LOG.info("cowardly refusing to overwrite: %s", fn)
        sys.exit()
    nc = ncopen(fn, "w")
    nc.title = f"IEM Daily Reanalysis {ts.year}"
    nc.platform = "Grided Observations"
    nc.description = f"IEM daily analysis on a {gridnav.dx} degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", gridnav.ny)
    nc.createDimension("lon", gridnav.nx)
    nc.createDimension("nv", 2)
    days = 2 if ci else ((ts.replace(year=ts.year + 1)) - ts).days
    nc.createDimension("time", int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat.bounds = "lat_bnds"
    # These are the grid centers
    lat[:] = gridnav.y_points
    lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "nv"))
    lat_bnds[:, 0] = gridnav.y_edges[:-1]
    lat_bnds[:, 1] = gridnav.y_edges[1:]

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon.bounds = "lon_bnds"
    # These are the grid centers
    lon[:] = gridnav.x_points

    lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "nv"))
    lon_bnds[:, 0] = gridnav.x_edges[:-1]
    lon_bnds[:, 1] = gridnav.x_edges[1:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {ts.year}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    # Tracked variables
    hasdata = nc.createVariable("hasdata", np.int8, ("lat", "lon"))
    hasdata.units = "1"
    hasdata.long_name = "Analysis Available for Grid Cell"
    hasdata.coordinates = "lon lat"
    hasdata[:] = 0

    high = nc.createVariable(
        "high_tmpk", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    high.units = "K"
    high.scale_factor = 0.01
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable(
        "low_tmpk", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    low.units = "K"
    low.scale_factor = 0.01
    low.long_name = "2m Air Temperature Daily Low"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    high12 = nc.createVariable(
        "high_tmpk_12z", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    high12.units = "K"
    high12.scale_factor = 0.01
    high12.long_name = "2m Air Temperature 24 Hour Max at 12 UTC"
    high12.standard_name = "2m Air Temperature"
    high12.coordinates = "lon lat"

    low12 = nc.createVariable(
        "low_tmpk_12z", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    low12.units = "K"
    low12.scale_factor = 0.01
    low12.long_name = "2m Air Temperature 12 Hour Min at 12 UTC"
    low12.standard_name = "2m Air Temperature"
    low12.coordinates = "lon lat"

    p01d = nc.createVariable(
        "p01d", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    p01d.units = "mm"
    p01d.scale_factor = 0.01
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    p01d12 = nc.createVariable(
        "p01d_12z", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    p01d12.units = "mm"
    p01d12.scale_factor = 0.01
    p01d12.long_name = "Precipitation"
    p01d12.standard_name = "Precipitation"
    p01d12.coordinates = "lon lat"
    p01d12.description = "24 Hour Precipitation Ending 12 UTC"

    # 0 -> 65535  so 0 to 6553.5
    rsds = nc.createVariable(
        "rsds", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    rsds.units = "W m-2"
    rsds.scale_factor = 0.1
    rsds.long_name = "surface_downwelling_shortwave_flux_in_air"
    rsds.standard_name = "surface_downwelling_shortwave_flux_in_air"
    rsds.coordinates = "lon lat"
    rsds.description = "Global Shortwave Irradiance"

    snow = nc.createVariable(
        "snow_12z", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    snow.units = "mm"
    snow.scale_factor = 0.01
    snow.long_name = "Snowfall"
    snow.standard_name = "Snowfall"
    snow.coordinates = "lon lat"
    snow.description = "Snowfall accumulation for the day"

    # 0 to 6553.5
    snowd = nc.createVariable(
        "snowd_12z", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    snowd.units = "mm"
    snowd.scale_factor = 0.1
    snowd.long_name = "Snow Depth"
    snowd.standard_name = "Snow Depth"
    snowd.coordinates = "lon lat"
    snowd.description = "Snow depth at time of observation"

    v1 = nc.createVariable(
        "avg_dwpk", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    v1.units = "K"
    v1.scale_factor = 0.01
    v1.long_name = "2m Average Dew Point Temperature"
    v1.standard_name = "Dewpoint"
    v1.coordinates = "lon lat"
    v1.description = "Dew Point average computed by averaging mixing ratios"

    v2 = nc.createVariable(
        "wind_speed", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    v2.units = "m s-1"
    v2.scale_factor = 0.001
    v2.long_name = "Wind Speed"
    v2.standard_name = "Wind Speed"
    v2.coordinates = "lon lat"
    v2.description = "Daily averaged wind speed magnitude"

    # 0 to 65535 so 0 to 65.535
    v1 = nc.createVariable(
        "power_swdn", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    v1.scale_factor = 0.001
    v1.units = "MJ d-1"
    v1.long_name = "All Sky Insolation Incident on a Horizontal Surface"
    v1.standard_name = "All Sky Insolation Incident on a Horizontal Surface"
    v1.coordinates = "lon lat"
    v1.description = "from NASA POWER"

    v1 = nc.createVariable(
        "high_soil4t", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    v1.units = "K"
    v1.scale_factor = 0.01
    v1.long_name = "4inch Soil Temperature Daily High"
    v1.standard_name = "4inch Soil Temperature"
    v1.coordinates = "lon lat"

    v1 = nc.createVariable(
        "low_soil4t", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    v1.units = "K"
    v1.scale_factor = 0.01
    v1.long_name = "4inch Soil Temperature Daily Low"
    v1.standard_name = "4inch Soil Temperature"
    v1.coordinates = "lon lat"

    v1 = nc.createVariable(
        "min_rh", np.ubyte, ("time", "lat", "lon"), fill_value=255
    )
    v1.units = "%"
    v1.scale_factor = 0.5
    v1.long_name = "Minimum Relative Humidity"
    v1.standard_name = "Minimum Relative Humidity"
    v1.coordinates = "lon lat"

    v1 = nc.createVariable(
        "max_rh", np.ubyte, ("time", "lat", "lon"), fill_value=255
    )
    v1.units = "%"
    v1.scale_factor = 0.5
    v1.long_name = "Maximum Relative Humidity"
    v1.standard_name = "Maximum Relative Humidity"
    v1.coordinates = "lon lat"

    nc.close()


@click.command()
@click.option("--year", type=int, required=True, help="Year to initialize")
@click.option("--domain", default="", help="IEMRE Domain to run for")
@click.option("--ci", is_flag=True, help="Run in CI mode")
def main(year: int, domain: str, ci: bool):
    """Go Main Go"""
    init_year(datetime(year, 1, 1), domain, ci)
    if ci:
        with ncopen(get_daily_ncname(year, domain), "a") as nc:
            for vname in "p01d p01d_12z snow_12z snowd_12z".split():
                nc.variables[vname][:] = 0


if __name__ == "__main__":
    main()
