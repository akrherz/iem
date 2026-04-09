"""Copy GFS grib data to IEMRE grid...

Run from RUN_50_AFTER.sh
"""

import shutil
import subprocess
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
import numpy as np
import pygrib
from affine import Affine
from pyiem.grid.nav import get_nav
from pyiem.iemre import DOMAINS as IEMRE_DOMAINS
from pyiem.iemre import reproject2iemre
from pyiem.reference import EPSG, ISO8601
from pyiem.util import logger, ncopen, utc

LOG = logger()
warnings.simplefilter("ignore", RuntimeWarning)


def create(ts: datetime, domain: str, dom: dict) -> str:
    """
    Create a new NetCDF file for a year of our specification!
    """
    dd = "" if domain == "conus" else f"_{domain}"
    gridnav = get_nav("iemre", domain)
    fn = f"/mesonet/data/iemre{dd}/gfs_current{dd}_new.nc"
    if Path(fn).exists():
        LOG.warning("File %s already exists, clobbering", fn)
        Path(fn).unlink()
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
        nc.createDimension("nv", 2)

        # Setup Coordinate Variables
        lat = nc.createVariable("lat", float, ("lat"))
        lat.units = "degrees_north"
        lat.long_name = "Latitude"
        lat.standard_name = "latitude"
        lat.bounds = "lat_bnds"
        lat.axis = "Y"
        lat[:] = gridnav.y_points

        lat_bnds = nc.createVariable("lat_bnds", float, ("lat", "nv"))
        lat_bnds[:, 0] = gridnav.y_edges[:-1]
        lat_bnds[:, 1] = gridnav.y_edges[1:]

        lon = nc.createVariable("lon", float, ("lon"))
        lon.units = "degrees_east"
        lon.long_name = "Longitude"
        lon.standard_name = "longitude"
        lon.bounds = "lon_bnds"
        lon.axis = "X"
        lon[:] = gridnav.x_points

        lon_bnds = nc.createVariable("lon_bnds", float, ("lon", "nv"))
        lon_bnds[:, 0] = gridnav.x_edges[:-1]
        lon_bnds[:, 1] = gridnav.x_edges[1:]

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

        # Soil Temperature
        ncvar = nc.createVariable(
            "tsoil", np.uint16, ("time", "lat", "lon"), fill_value=65535
        )
        ncvar.units = "K"
        ncvar.scale_factor = 0.01
        ncvar.long_name = "0-10 cm Average Soil Temperature"
        ncvar.standard_name = "0-10 cm Average Soil Temperature"
        ncvar.coordinates = "lon lat"

        # Soil Moisture, 255 levels, 0.25 resolution, so 0 to 63.75 mm
        ncvar = nc.createVariable(
            "soil_moisture", np.uint8, ("time", "lat", "lon"), fill_value=255
        )
        ncvar.units = "mm"
        ncvar.scale_factor = 0.25
        ncvar.long_name = "0-10 cm Average Soil Moisture"
        ncvar.standard_name = "0-10 cm Average Soil Moisture"
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


def merge_grib(nc, now, domain: str, dom: dict):
    """Merge what grib data we can find into the netcdf file."""
    # Tricky here for how to compute a valid date
    # iemre US 2024-08-05 -> 2024-08-06  6 UTC
    # sa      2024-08-05 -> 2024-08-06  6 UTC  Don't have hourly
    # europe   2024-08-05 -> 2024-08-06  0 UTC
    # china    2024-08-05 -> 2024-08-05 18 UTC
    write_hour = {
        "conus": 6,
        "sa": 6,
        "europe": 0,
        "china": 18,
    }

    tmaxgrid = None
    tmingrid = None
    tsoilgrid = None
    smgrid = None
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
                dx = grb["iDirectionIncrementInDegrees"]
                # the grib data is top down
                affine = Affine(
                    dx,
                    0.0,
                    0 - dx / 2.0,
                    0.0,
                    -dx,
                    min(
                        grb["latitudeOfFirstGridPointInDegrees"] + dx / 2.0,
                        89.99,
                    ),
                )
            name = grb.shortName.lower()
            # Chris Farley no-idea, otherwise get no-data stripe at 0° Lon
            if dom == "europe":
                values = grb.values
            else:
                values = grb.values[:-1, :-1]
            if name == "tmax":
                if tmaxgrid is None:
                    tmaxgrid = values
                else:
                    tmaxgrid = np.where(values > tmaxgrid, values, tmaxgrid)
            elif name in ["dswrf", "sdswrf"]:
                if srad is None:
                    # Average 6 hour flux in W/m^2 to MJ/day
                    srad = values * 6.0 * 3600.0 / 1_000_000.0
                else:
                    srad = srad + (values * 6.0 * 3600.0 / 1_000_000.0)
            elif name == "tmin":
                if tmingrid is None:
                    tmingrid = values
                else:
                    tmingrid = np.where(values < tmingrid, values, tmingrid)
            elif name == "prate":
                hits += 1
                # kg/m^2/s over six hours
                ptotal = values * 6.0 * 3600.0
                if plast is None:
                    plast = 0
                if pgrid is None:
                    pgrid = 0
                pgrid = pgrid + (ptotal - plast)
                plast = ptotal
            # Hacky
            elif name == "st" and str(grb).find("0.0-0.1 m") > -1:
                if tsoilgrid is None:
                    tsoilgrid = values
                else:
                    tsoilgrid += values
            elif name == "soilw" and str(grb).find("0.0-0.1 m") > -1:
                # Values of 1 are common/water, which overflows our storage
                # convert to mm depth
                values = np.where(values == 1, np.nan, values * 100.0)
                if smgrid is None:
                    smgrid = values
                else:
                    smgrid += values

        grbs.close()

        # Write out the data at the reset time
        if fxtime.hour == write_hour[domain]:
            approxlocal = (fxtime - timedelta(hours=6)).astimezone(
                dom["tzinfo"]
            )
            days = (approxlocal.date() - now.date()).days
            if hits == 4:
                nc.variables["high_tmpk"][days] = reproject2iemre(
                    tmaxgrid, affine, EPSG[4326], domain=domain
                )
                nc.variables["low_tmpk"][days] = reproject2iemre(
                    tmingrid, affine, EPSG[4326], domain=domain
                )
                nc.variables["p01d"][days] = reproject2iemre(
                    pgrid, affine, EPSG[4326], domain=domain
                )
                pout = np.ma.array(nc.variables["p01d"][days])
                nc.variables["tsoil"][days] = reproject2iemre(
                    tsoilgrid / 4.0, affine, EPSG[4326], domain=domain
                )
                nc.variables["soil_moisture"][days] = reproject2iemre(
                    smgrid / 4.0, affine, EPSG[4326], domain=domain
                )
                nc.variables["srad"][days] = reproject2iemre(
                    srad, affine, EPSG[4326], domain=domain
                )
                sout = np.ma.array(nc.variables["srad"][days])
                LOG.info(
                    "Writing %s[localdate:%s], day=%s, domain=%s "
                    "srad:%.1f->%.1f pgrid:%.2f->%.2f",
                    fxtime,
                    approxlocal.date(),
                    days,
                    domain,
                    -1 if srad is None else np.nanmean(srad),  # appease linter
                    np.ma.mean(sout),
                    -1 if pgrid is None else np.nanmean(pgrid),
                    np.ma.mean(pout),
                )
            tmingrid = None
            tmaxgrid = None
            tsoilgrid = None
            smgrid = None
            srad = None
            hits = 0


@click.command()
@click.option("--valid", type=click.DateTime(), help="Specify UTC valid time")
@click.option("--domain", default="", help="Run just for domain")
def main(valid: datetime, domain: str):
    """Do the work."""
    valid = valid.replace(tzinfo=timezone.utc)
    # Run every hour, filter those we don't run
    if valid.hour % 6 != 0:
        return
    for thisdomain, dom in IEMRE_DOMAINS.items():
        if domain not in ("", thisdomain):
            LOG.info("Skipping %s domain due to CLI args", thisdomain)
            continue
        ncfn = create(valid, thisdomain, dom)
        with ncopen(ncfn, "a") as nc:
            merge_grib(nc, valid, thisdomain, dom)
        dd = "" if thisdomain == "conus" else f"_{thisdomain}"
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
