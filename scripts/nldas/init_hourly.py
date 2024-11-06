"""Generate the NLDASv2 hourly analysis file for a year"""

import os
from datetime import datetime

import click
import numpy as np
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    ncfn = f"/mesonet/data/nldas/{ts.year}_hourly.nc"
    if os.path.isfile(ncfn):
        LOG.info("Cowardly refusing to overwrite: %s", ncfn)
        return
    nc = ncopen(ncfn, "w")
    nc.title = f"NLDASv2 NOAH Hourly Reanalysis {ts.year}"
    nc.platform = "Grided Observations"
    nc.description = "NLDASv2 hourly analysis"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", 224)
    nc.createDimension("lon", 464)
    ts2 = datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    LOG.info("Year %s has %s days", ts.year, days)
    nc.createDimension("time", int(days) * 24)
    nc.createDimension("soil_level", 4)

    ncv = nc.createVariable("soil_level", float, ("soil_level",))
    ncv.units = "m"
    ncv.description = "Depths of centers of soil layers"
    # midpoints
    ncv[:] = [0.05, 0.25, 0.7, 1.5]

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = np.arange(25.0625, 52.99, 0.125)

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = np.arange(-124.9375, -67.01, 0.125)

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Hours since {ts.year}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days) * 24)

    # NOTE: Condensation is + and Evapration is -
    # -128 to 127 for -25 to 25 `ACETLSM`
    ncv = nc.createVariable(
        "evap", np.int8, ("time", "lat", "lon"), fill_value=127
    )
    ncv.units = "mm"
    ncv.scale_factor = 0.4
    ncv.long_name = "Evaporation"
    ncv.standard_name = "Evaporation"
    ncv.coordinates = "lon lat"
    ncv.description = "Evaporation for the hour valid time"

    # 0 -> 65535 so 0 to 1966 `ACSWDNLSM`
    ncv = nc.createVariable(
        "rsds",
        np.uint16,
        ("time", "lat", "lon"),
        fill_value=65535,
    )
    ncv.units = "W m-2"
    ncv.scale_factor = 0.03
    ncv.long_name = "surface_downwelling_shortwave_flux_in_air"
    ncv.standard_name = "surface_downwelling_shortwave_flux_in_air"
    ncv.coordinates = "lon lat"
    ncv.description = "Global Shortwave Irradiance"

    # 0->255 [213 333] `TSLB`
    ncv = nc.createVariable(
        "soilt",
        np.uint8,
        ("time", "soil_level", "lat", "lon"),
        fill_value=255,
    )
    ncv.units = "K"
    ncv.add_offset = 213.0
    ncv.scale_factor = 0.5
    ncv.long_name = "Soil Temperature"
    ncv.standard_name = "Soil Temperature"
    ncv.coordinates = "lon lat"

    # 0->255 [0 0.8] Hope this works? `SMOIS`
    ncv = nc.createVariable(
        "soilm",
        np.uint8,
        ("time", "soil_level", "lat", "lon"),
        fill_value=255,
    )
    ncv.units = "m^3 m^-3"
    ncv.scale_factor = 0.0031
    ncv.long_name = "Volumetric Soil Moisture"
    ncv.standard_name = "Volumetric Soil Moisture"
    ncv.coordinates = "lon lat"

    nc.close()


@click.command()
@click.option("--year", type=int, required=True)
def main(year: int):
    """Go Main Go"""
    init_year(datetime(year, 1, 1))


if __name__ == "__main__":
    main()
