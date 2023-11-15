"""Generate the CONUS404 hourly analysis file for a year"""
import datetime
import os
import sys

import numpy as np
from pyiem.util import logger, ncopen

LOG = logger()


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    #  wget -O /tmp/wrfconstants_usgs404.nc
    # https://data.rda.ucar.edu/ds559.0/INVARIANT/wrfconstants_usgs404.nc
    tplnc = ncopen("/tmp/wrfconstants_usgs404.nc")

    ncfn = f"/mesonet/data/conus404/{ts.year}_hourly.nc"
    if os.path.isfile(ncfn):
        LOG.info("Cowardly refusing to overwrite: %s", ncfn)
        return
    nc = ncopen(ncfn, "w")
    nc.title = f"CONUS404 Hourly Reanalysis {ts.year}"
    nc.platform = "Grided Observations"
    nc.description = "CONUS404 hourly analysis"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{datetime.datetime.now():%d %B %Y} Generated"
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension("south_north", tplnc.dimensions["south_north"].size)
    nc.createDimension("west_east", tplnc.dimensions["west_east"].size)
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    LOG.info("Year %s has %s days", ts.year, days)
    nc.createDimension("time", int(days) * 24)
    nc.createDimension("soil_level", 4)

    ncv = nc.createVariable("soil_level", float, ("soil_level",))
    ncv.units = "m"
    ncv.description = "Depths of centers of soil layers"
    # midpoints
    ncv[:] = tplnc.variables["ZS"][:]

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("south_north", "west_east"))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = tplnc.variables["XLAT"][:]

    lon = nc.createVariable("lon", float, ("south_north", "west_east"))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = tplnc.variables["XLONG"][:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Hours since {ts.year}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days) * 24)

    # 0->65535 `T2`
    tmpk = nc.createVariable(
        "tmpk",
        np.uint16,
        ("time", "south_north", "west_east"),
        fill_value=65535,
    )
    tmpk.units = "K"
    tmpk.scale_factor = 0.01
    tmpk.long_name = "2m Air Temperature"
    tmpk.standard_name = "2m Air Temperature"
    tmpk.coordinates = "lon lat"

    # 0->65535  0 to 655.35 `TD2`
    dwpk = nc.createVariable(
        "dwpk",
        np.uint16,
        ("time", "south_north", "west_east"),
        fill_value=65335,
    )
    dwpk.units = "K"
    dwpk.scale_factor = 0.01
    dwpk.long_name = "2m Air Dew Point Temperature"
    dwpk.standard_name = "2m Air Dew Point Temperature"
    dwpk.coordinates = "lon lat"

    # NOTE: we need to store negative numbers here, gasp
    # -32768 to 32767 so -98 to 98 mps `U10`
    uwnd = nc.createVariable(
        "uwnd",
        np.int16,
        ("time", "south_north", "west_east"),
        fill_value=32767,
    )
    uwnd.scale_factor = 0.003
    uwnd.units = "meters per second"
    uwnd.long_name = "U component of the wind"
    uwnd.standard_name = "U component of the wind"
    uwnd.coordinates = "lon lat"

    # NOTE: we need to store negative numbers here, gasp
    # -32768 to 32767 so -98 to 98 mps `V10`
    vwnd = nc.createVariable(
        "vwnd",
        np.int16,
        ("time", "south_north", "west_east"),
        fill_value=32767,
    )
    vwnd.scale_factor = 0.003
    vwnd.units = "meters per second"
    vwnd.long_name = "V component of the wind"
    vwnd.standard_name = "V component of the wind"
    vwnd.coordinates = "lon lat"

    # 0->65535  0 to 327.675 `PREC_ACC_NC`
    p01m = nc.createVariable(
        "p01m",
        np.uint16,
        ("time", "south_north", "west_east"),
        fill_value=65535,
    )
    p01m.units = "mm"
    p01m.scale_factor = 0.005
    p01m.long_name = "Precipitation"
    p01m.standard_name = "Precipitation"
    p01m.coordinates = "lon lat"
    p01m.description = "Precipitation accumulation for the hour valid time"

    # NOTE: Condensation is + and Evapration is -
    # -128 to 127 for -25 to 25 `ACETLSM`
    ncv = nc.createVariable(
        "evap", np.int8, ("time", "south_north", "west_east"), fill_value=127
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
        ("time", "south_north", "west_east"),
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
        ("time", "soil_level", "south_north", "west_east"),
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
        ("time", "soil_level", "south_north", "west_east"),
        fill_value=255,
    )
    ncv.units = "m^3 m^-3"
    ncv.scale_factor = 0.0031
    ncv.long_name = "Volumetric Soil Moisture"
    ncv.standard_name = "Volumetric Soil Moisture"
    ncv.coordinates = "lon lat"

    nc.close()


def main(argv):
    """Go Main Go"""
    year = int(argv[1])
    init_year(datetime.datetime(year, 1, 1))


if __name__ == "__main__":
    main(sys.argv)
