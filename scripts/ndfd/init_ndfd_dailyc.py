"""Generate the NDFD climatology file, hmmm"""
import datetime
import os

import numpy as np
import pygrib
from pyiem.util import ncopen


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    ncfn = "/mesonet/data/ndfd/ndfd_dailyc.nc"
    if os.path.isfile(ncfn):
        print(f"Cowardly refusing to overwrite {ncfn}")
        return
    nc = ncopen(ncfn, "w")
    nc.title = "NDFD"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (
        datetime.datetime.now().strftime("%d %B %Y"),
    )

    grbs = pygrib.open(
        "/mesonet/ARCHIVE/data/2019/05/06/model/ndfd/"
        "00/ndfd.t00z.awp2p5f001.grib2"
    )
    grb = grbs[1]
    shape = grb.values.shape
    lats, lons = grb.latlons()

    # Setup Dimensions
    nc.createDimension("lat", shape[0])
    nc.createDimension("lon", shape[1])
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension("time", int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat", "lon"))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.bounds = "lat_bnds"
    lat.axis = "Y"
    lat[:] = lats

    lon = nc.createVariable("lon", float, ("lat", "lon"))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = lons

    tm = nc.createVariable("time", float, ("time",))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "p01d", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    p01d.units = "mm"
    p01d.scale_factor = 0.01
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

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

    gdd = nc.createVariable(
        "gdd50", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    gdd.units = "F"
    gdd.scale_factor = 0.01
    gdd.long_name = "Growing Degree Days"
    gdd.standard_name = "Growing Degree Days"
    gdd.coordinates = "lon lat"

    nc.close()


def main():
    """Go Main"""
    init_year(datetime.datetime(2000, 1, 1))


if __name__ == "__main__":
    main()
