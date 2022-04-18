"""Copy NDFD grib data to IEMRE...

Run from RUN_20_AFTER.sh
"""
import os
from datetime import timedelta, date
import shutil

import pygrib
import numpy as np
from scipy.interpolate import NearestNDInterpolator
from pyiem import iemre
from pyiem.util import utc, ncopen, logger

LOG = logger()


def create(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    fn = "/mesonet/data/iemre/ndfd_current_new.nc"
    with ncopen(fn, "w") as nc:
        nc.title = "NDFD on IEMRE Grid."
        nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
        nc.ndfd_forecast = f"{ts:%Y-%m-%dT%H:%M:%SZ}"
        nc.history = f"{date.today():%d %B %Y} Generated"

        # Setup Dimensions
        nc.createDimension("lat", iemre.NY)
        nc.createDimension("lon", iemre.NX)
        # store 20 days worth, to be safe of future changes
        nc.createDimension("time", 20)

        # Setup Coordinate Variables
        lat = nc.createVariable("lat", float, ("lat"))
        lat.units = "degrees_north"
        lat.long_name = "Latitude"
        lat.standard_name = "latitude"
        lat.bounds = "lat_bnds"
        lat.axis = "Y"
        lat[:] = iemre.YAXIS

        lon = nc.createVariable("lon", float, ("lon"))
        lon.units = "degrees_east"
        lon.long_name = "Longitude"
        lon.standard_name = "longitude"
        lon.bounds = "lon_bnds"
        lon.axis = "X"
        lon[:] = iemre.XAXIS

        tm = nc.createVariable("time", float, ("time",))
        tm.units = f"Days since {ts:%Y-%m-%d} 00:00:0.0"
        tm.long_name = "Time"
        tm.standard_name = "time"
        tm.axis = "T"
        tm.calendar = "gregorian"
        # Placeholder
        tm[:] = np.arange(0, 20)

        high = nc.createVariable(
            "high_tmpk", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        high.units = "K"
        high.scale_factor = 0.01
        high.long_name = "2m Air Temperature 12 Hour High"
        high.standard_name = "2m Air Temperature"
        high.coordinates = "lon lat"

        low = nc.createVariable(
            "low_tmpk", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        low.units = "K"
        low.scale_factor = 0.01
        low.long_name = "2m Air Temperature 12 Hour Low"
        low.standard_name = "2m Air Temperature"
        low.coordinates = "lon lat"


def do_target(nc, now, target, day, xi, yi, vname):
    """Make magic."""
    hour = 0
    found = False
    lons = None
    lats = None
    ncvar = "high" if vname == "Maximum" else "low"
    while hour < 24 and not found:
        ts = now - timedelta(hours=hour)
        fhour = (target - ts).total_seconds() / 3600.0
        testfn = ts.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/ndfd/"
            f"%H/ndfd.t%Hz.awp2p5f{fhour:03.0f}.grib2"
        )
        if not os.path.isfile(testfn):
            hour += 1
            continue
        grbs = pygrib.open(testfn)
        for grb in grbs:
            if lons is None:
                lats, lons = [np.ravel(ar) for ar in grb.latlons()]
            if (
                grb.valid_key("parameterName")
                and grb["parameterName"] == f"{vname} temperature"
            ):
                # This is 0z
                LOG.info("%s_tmpk day: %s fn: %s", ncvar, day, testfn)
                nn = NearestNDInterpolator((lons, lats), np.ravel(grb.values))
                nc.variables[f"{ncvar}_tmpk"][day, :, :] = nn(xi, yi)
                found = True
        grbs.close()
        hour += 1


def merge_grib(nc, now):
    """Merge what grib data we can find into the netcdf file."""

    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    for day in range(10):
        dt = now.date() + timedelta(days=day)
        # Look backward until we find a 0z forecast (utc + 1 day)
        target = utc(dt.year, dt.month, dt.day, 0, 0, 0) + timedelta(days=1)
        do_target(nc, now, target, day, xi, yi, "Maximum")
        # Look backward until we find a 12z forecast
        target = utc(dt.year, dt.month, dt.day, 12, 0, 0)
        do_target(nc, now, target, day, xi, yi, "Minimum")


def main():
    """Do the work."""
    now = utc().replace(minute=0, second=0, microsecond=0)
    create(now)
    with ncopen("/mesonet/data/iemre/ndfd_current_new.nc", "a") as nc:
        merge_grib(nc, now)
    shutil.move(
        "/mesonet/data/iemre/ndfd_current_new.nc",
        "/mesonet/data/iemre/ndfd_current.nc",
    )


if __name__ == "__main__":
    main()
