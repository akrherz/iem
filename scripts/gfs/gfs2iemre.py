"""Copy GFS grib data to IEMRE grid...

Run from RUN_50_AFTER.sh
"""

import shutil
import subprocess
from datetime import date, timedelta, timezone

import click
import numpy as np
import pygrib
from pyiem import iemre
from pyiem.reference import ISO8601
from pyiem.util import logger, ncopen, utc
from scipy.interpolate import NearestNDInterpolator

LOG = logger()


def create(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """
    fn = "/mesonet/data/iemre/gfs_current_new.nc"
    with ncopen(fn, "w") as nc:
        nc.title = "GFS on IEMRE Grid."
        nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
        nc.gfs_forecast = ts.strftime(ISO8601)
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

        ncvar = nc.createVariable(
            "tsoil", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        ncvar.units = "K"
        ncvar.scale_factor = 0.01
        ncvar.long_name = "0-10 cm Average Soil Temperature"
        ncvar.standard_name = "0-10 cm Average Soil Temperature"
        ncvar.coordinates = "lon lat"

        ncvar = nc.createVariable(
            "p01d", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        ncvar.units = "mm"
        ncvar.scale_factor = 0.01
        ncvar.long_name = "Precipitation Accumulation"
        ncvar.standard_name = "precipitation_amount"
        ncvar.coordinates = "lon lat"


def merge_grib(nc, now):
    """Merge what grib data we can find into the netcdf file."""

    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    lons = None
    lats = None
    tmaxgrid = None
    tmingrid = None
    tsoilgrid = None
    pgrid = None
    hits = 0
    for fhour in range(6, 385, 6):
        fxtime = now + timedelta(hours=fhour)
        grbfn = now.strftime(
            f"/mesonet/tmp/gfs/%Y%m%d%H/gfs.t%Hz.sfluxgrbf{fhour:03.0f}.grib2"
        )
        grbs = pygrib.open(grbfn)
        for grb in grbs:
            name = grb.shortName.lower()
            if lons is None:
                lats, lons = [np.ravel(x) for x in grb.latlons()]
                lons = np.where(lons > 180, lons - 360, lons)
            if name == "tmax":
                if tmaxgrid is None:
                    tmaxgrid = grb.values
                else:
                    tmaxgrid = np.where(
                        grb.values > tmaxgrid, grb.values, tmaxgrid
                    )
            elif name == "tmin":
                if tmingrid is None:
                    tmingrid = grb.values
                else:
                    tmingrid = np.where(
                        grb.values < tmingrid, grb.values, tmingrid
                    )
            elif name == "prate":
                # kg/m^2/s over six hours
                hits += 1
                if pgrid is None:
                    pgrid = grb.values * 6.0 * 3600
                else:
                    pgrid += grb.values * 6.0 * 3600
            # Hacky
            elif name == "st" and str(grb).find("0.0-0.1 m") > -1:
                if tsoilgrid is None:
                    tsoilgrid = grb.values
                else:
                    tsoilgrid += grb.values

        grbs.close()

        # Write tmax, tmin out at 6z
        if fxtime.hour == 6:
            # The actual date is minus one
            days = (fxtime.date() - now.date()).days - 1
            if hits == 4:
                LOG.info("Writing %s, days=%s", fxtime, days)
                nn = NearestNDInterpolator((lons, lats), np.ravel(tmaxgrid))
                nc.variables["high_tmpk"][days, :, :] = nn(xi, yi)
                nn = NearestNDInterpolator((lons, lats), np.ravel(tmingrid))
                nc.variables["low_tmpk"][days, :, :] = nn(xi, yi)
                nn = NearestNDInterpolator((lons, lats), np.ravel(pgrid))
                nc.variables["p01d"][days, :, :] = nn(xi, yi)
                nn = NearestNDInterpolator(
                    (lons, lats), np.ravel(tsoilgrid / 4.0)
                )
                nc.variables["tsoil"][days, :, :] = nn(xi, yi)
            tmingrid = None
            tmaxgrid = None
            tsoilgrid = None
            hits = 0


@click.command()
@click.option("--valid", type=click.DateTime(), help="Specify UTC valid time")
def main(valid):
    """Do the work."""
    valid = valid.replace(tzinfo=timezone.utc)
    # Run every hour, filter those we don't run
    if valid.hour % 6 != 0:
        return
    create(valid)
    with ncopen("/mesonet/data/iemre/gfs_current_new.nc", "a") as nc:
        merge_grib(nc, valid)
    shutil.move(
        "/mesonet/data/iemre/gfs_current_new.nc",
        "/mesonet/data/iemre/gfs_current.nc",
    )
    # Archive this as we need it for various projects
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"data a {valid:%Y%m%d%H%M} bogus "
            f"model/gfs/gfs_{valid:%Y%m%d%H}_iemre.nc nc"
        ),
        "/mesonet/data/iemre/gfs_current.nc",
    ]
    subprocess.call(cmd)

    # Generate 4inch plots based on 6z GFS
    if valid.hour == 6 and (utc() - valid).days < 2:
        subprocess.call(["python", "gfs_4inch.py"])


if __name__ == "__main__":
    main()
