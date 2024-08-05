"""Copy GFS grib data to IEMRE grid...

Run from RUN_50_AFTER.sh
"""

import shutil
import subprocess
import warnings
from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pygrib
from affine import Affine
from pyiem import iemre
from pyiem.reference import EPSG, ISO8601
from pyiem.util import logger, ncopen, utc

LOG = logger()
warnings.simplefilter("ignore", RuntimeWarning)


def create(ts: datetime, domain: str, dom: dict) -> str:
    """
    Create a new NetCDF file for a year of our specification!
    """
    dd = "" if domain == "" else f"_{domain}"
    fn = f"/mesonet/data/iemre/gfs_current{dd}_new.nc"
    with ncopen(fn, "w") as nc:
        nc.title = (
            f"GFS on IEMRE Grid for Domain: {domain}. Approximating a date "
            f"for {dom['tzinfo']}."
        )
        nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
        nc.gfs_forecast = ts.strftime(ISO8601)
        nc.history = f"{utc():%Y-%m-%dT%H:%M:%S} UTC Generated"

        # Setup Dimensions
        nc.createDimension("lat", dom["ny"])
        nc.createDimension("lon", dom["nx"])
        # store 20 days worth, to be safe of future changes
        nc.createDimension("time", 20)

        # Setup Coordinate Variables
        lat = nc.createVariable("lat", float, ("lat"))
        lat.units = "degrees_north"
        lat.long_name = "Latitude"
        lat.standard_name = "latitude"
        lat.bounds = "lat_bnds"
        lat.axis = "Y"
        lat[:] = np.arange(dom["south"], dom["north"], iemre.DY)

        lon = nc.createVariable("lon", float, ("lon"))
        lon.units = "degrees_east"
        lon.long_name = "Longitude"
        lon.standard_name = "longitude"
        lon.bounds = "lon_bnds"
        lon.axis = "X"
        lon[:] = np.arange(dom["west"], dom["east"], iemre.DX)

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

        ncvar = nc.createVariable(
            "srad", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        ncvar.scale_factor = 0.001
        ncvar.units = "MJ d-1"
        ncvar.long_name = "Solar Radiation"
        ncvar.standard_name = "surface_downwelling_shortwave_flux_in_air"
        ncvar.coordinates = "lon lat"
        ncvar.description = "from NASA POWER"

    return fn


def shuffle(grid):
    """Convert the 0-360 grid to -180 to 180."""
    return np.concatenate((grid[:, 1536:], grid[:, :1536]), axis=1)


def merge_grib(nc, now, domain: str, dom: dict):
    """Merge what grib data we can find into the netcdf file."""
    # Tricky here for how to compute a valid date
    # iemre US 2024-08-05 -> 2024-08-06  6 UTC
    # europe   2024-08-05 -> 2024-08-06  0 UTC
    # china    2024-08-05 -> 2024-08-05 18 UTC
    write_hour = {
        "": 6,
        "europe": 0,
        "china": 18,
    }

    tmaxgrid = None
    tmingrid = None
    tsoilgrid = None
    pgrid = None
    plast = None
    ptotal = None
    srad = None
    hits = 0
    affine = None
    for fhour in range(6, 385, 6):
        fxtime = now + timedelta(hours=fhour)
        grbfn = now.strftime(
            f"/mesonet/tmp/gfs/%Y%m%d%H/gfs.t%Hz.sfluxgrbf{fhour:03.0f}.grib2"
        )
        grbs = pygrib.open(grbfn)
        for grb in grbs:
            if affine is None:
                affine = Affine(0.125, 0, -180, 0, -0.125, 89.9103)
            name = grb.shortName.lower()
            if name == "tmax":
                if tmaxgrid is None:
                    tmaxgrid = grb.values
                else:
                    tmaxgrid = np.where(
                        grb.values > tmaxgrid, grb.values, tmaxgrid
                    )
            elif name == "dswrf":
                if srad is None:
                    # Average 6 hour flux in W/m^2 to MJ/day
                    srad = grb.values * 6.0 * 3600.0 / 1_000_000.0
                else:
                    srad = srad + (grb.values * 6.0 * 3600.0 / 1_000_000.0)
            elif name == "tmin":
                if tmingrid is None:
                    tmingrid = grb.values
                else:
                    tmingrid = np.where(
                        grb.values < tmingrid, grb.values, tmingrid
                    )
            elif name == "prate":
                hits += 1
                # kg/m^2/s over six hours
                ptotal = grb.values * 6.0 * 3600.0
                if plast is None:
                    plast = 0
                if pgrid is None:
                    pgrid = 0
                pgrid = pgrid + (ptotal - plast)
                plast = ptotal
            # Hacky
            elif name == "st" and str(grb).find("0.0-0.1 m") > -1:
                if tsoilgrid is None:
                    tsoilgrid = grb.values
                else:
                    tsoilgrid += grb.values

        grbs.close()

        # Write out the data at the reset time
        if fxtime.hour == write_hour[domain]:
            approxlocal = (fxtime - timedelta(hours=6)).astimezone(
                dom["tzinfo"]
            )
            days = (approxlocal.date() - now.date()).days
            if hits == 4:
                nc.variables["high_tmpk"][days] = iemre.reproject2iemre(
                    shuffle(tmaxgrid), affine, EPSG[4326], domain=domain
                )
                nc.variables["low_tmpk"][days] = iemre.reproject2iemre(
                    shuffle(tmingrid), affine, EPSG[4326], domain=domain
                )
                nc.variables["p01d"][days] = iemre.reproject2iemre(
                    shuffle(pgrid), affine, EPSG[4326], domain=domain
                )
                pout = nc.variables["p01d"][days]
                nc.variables["tsoil"][days] = iemre.reproject2iemre(
                    shuffle(tsoilgrid / 4.0), affine, EPSG[4326], domain=domain
                )
                nc.variables["srad"][days] = iemre.reproject2iemre(
                    shuffle(srad), affine, EPSG[4326], domain=domain
                )
                sout = nc.variables["srad"][days]
                LOG.info(
                    "Writing %s[localdate:%s], day=%s, domain=%s "
                    "srad:%.1f->%.1f pgrid:%.2f->%.2f",
                    fxtime,
                    approxlocal.date(),
                    days,
                    domain,
                    np.nanmean(srad),
                    np.ma.mean(sout),
                    np.nanmean(pgrid),
                    np.ma.mean(pout),
                )
            tmingrid = None
            tmaxgrid = None
            tsoilgrid = None
            srad = None
            hits = 0


@click.command()
@click.option("--valid", type=click.DateTime(), help="Specify UTC valid time")
def main(valid):
    """Do the work."""
    valid = valid.replace(tzinfo=timezone.utc)
    # Run every hour, filter those we don't run
    if valid.hour % 6 != 0:
        return
    for domain, dom in iemre.DOMAINS.items():
        ncfn = create(valid, domain, dom)
        with ncopen(ncfn, "a") as nc:
            merge_grib(nc, valid, domain, dom)
        dd = "" if domain == "" else f"_{domain}"
        # Archive this as we need it for various projects
        cmd = [
            "pqinsert",
            "-p",
            (
                f"data a {valid:%Y%m%d%H%M} bogus "
                f"model/gfs/gfs_{valid:%Y%m%d%H}_iemre{dd}.nc nc"
            ),
            ncfn,
        ]
        subprocess.call(cmd)
        shutil.move(ncfn, ncfn.replace("_new", ""))

    # Generate 4inch plots based on 6z GFS
    if valid.hour == 6 and (utc() - valid).days < 2:
        subprocess.call(["python", "gfs_4inch.py"])


if __name__ == "__main__":
    main()
