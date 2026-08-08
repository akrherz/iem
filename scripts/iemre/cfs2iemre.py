"""Download and process the CFS onto the IEMRE grid.

Run from RUN_NOON.sh for 2 days ago
"""

import os
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import click
import numpy as np
import pygrib
import requests
from metpy.calc import relative_humidity_from_specific_humidity
from metpy.units import units
from netCDF4 import Dataset
from pyiem.grid.nav import get_nav
from pyiem.iemre import DOMAINS, grb2iemre
from pyiem.util import exponential_backoff, logger, ncopen, utc
from tqdm import tqdm

LOG = logger()


def process2iemre(nc: Dataset, valid: datetime, domain: str):
    """Merge in the grib data"""
    t2_grbs = pygrib.open("t2.grb2")
    tmax_grbs = pygrib.open("tmax.grb2")
    tmin_grbs = pygrib.open("tmin.grb2")
    prate_grbs = pygrib.open("prate.grb2")
    dswsfc_grbs = pygrib.open("dswsfc.grb2")
    q2m_grbs = pygrib.open("q2m.grb2")

    nav = get_nav("iemre", domain)
    shp = (int(nav.ny), int(nav.nx))
    quorum = 0
    tmax_running = np.ones(shp) * 100.0
    tmin_running = np.ones(shp) * 400.0
    prate_running = np.zeros(shp)
    dswsfc_running = np.zeros(shp)
    rh_running = np.zeros(shp)

    time_index = nc.variables["time"][:].tolist()

    progress = tqdm(list(range(1, tmax_grbs.messages + 1)))
    for msgnum in progress:
        # Figure out the forecast itme
        ftime = valid + timedelta(hours=tmax_grbs[msgnum].forecastTime)
        # Get the values on our analysis grid
        t2 = grb2iemre(t2_grbs[msgnum], domain=domain)
        tmax = grb2iemre(tmax_grbs[msgnum], domain=domain)
        tmin = grb2iemre(tmin_grbs[msgnum], domain=domain)
        prate = grb2iemre(prate_grbs[msgnum], domain=domain) * 6 * 3600.0
        dswsfc = grb2iemre(dswsfc_grbs[msgnum], domain=domain)
        q2m = grb2iemre(q2m_grbs[msgnum], domain=domain)

        tmax_running = np.maximum(tmax_running, tmax)
        tmin_running = np.minimum(tmin_running, tmin)
        prate_running += prate
        dswsfc_running += dswsfc
        rh_running += (
            relative_humidity_from_specific_humidity(
                units("hPa") * 1000.0,
                units("degK") * t2,
                units("kg/kg") * q2m,
            )
            .to(units("percent"))
            .magnitude
        )
        quorum += 1
        if ftime.hour == 6:
            if quorum == 4:
                # This is off by one
                days = (ftime.date() - date(valid.year, 1, 1)).days - 1
                tidx = time_index.index(days)
                progress.write(f"Writing.... {ftime} tidx:{tidx}")
                nc.variables["high_tmpk"][tidx, :, :] = tmax_running
                nc.variables["low_tmpk"][tidx, :, :] = tmin_running
                nc.variables["p01d"][tidx, :, :] = prate_running
                nc.variables["srad"][tidx, :, :] = dswsfc_running / quorum
                nc.variables["avg_rh"][tidx, :, :] = rh_running / quorum

            # Reset
            tmax_running[:] = 100.0
            tmin_running[:] = 400.0
            prate_running[:] = 0.0
            dswsfc_running[:] = 0.0
            rh_running[:] = 0.0
            quorum = 0

    t2_grbs.close()
    tmax_grbs.close()
    tmin_grbs.close()
    prate_grbs.close()
    dswsfc_grbs.close()
    q2m_grbs.close()


def create_netcdf(valid: datetime, domain: str) -> str:
    """Create and return the netcdf file"""
    nc = ncopen("iemre.nc", "w")
    nc.title = f"IEM Regridded CFS Member 1 Forecast {valid:%Y}"
    nc.model_init = f"{valid:%Y-%m-%d %H:%M} UTC"
    nc.platform = "Grided Forecast"
    nc.description = "IEM Regridded CFS on 0.125 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = f"{utc():%d %B %Y} Generated"
    nc.comment = "No comment at this time"

    nav = get_nav("iemre", domain)

    # Setup Dimensions
    nc.createDimension("lat", nav.ny)
    nc.createDimension("lon", nav.nx)
    nc.createDimension("time", 310)  # approx and allow some wiggle room

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = nav.y_points

    lon = nc.createVariable("lon", float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = nav.x_points

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {valid.year}-01-01 00:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    d1 = (valid.date() - date(valid.year, 1, 1)).days
    tm[:] = np.arange(d1, d1 + 310)

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

    p01d = nc.createVariable(
        "p01d", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    p01d.units = "mm"
    p01d.scale_factor = 0.01
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    rh = nc.createVariable(
        "avg_rh", np.uint8, ("time", "lat", "lon"), fill_value=255
    )
    rh.units = "%"
    rh.long_name = "Average Relative Humidity"
    rh.standard_name = "relative_humidity"
    rh.coordinates = "lon lat"
    rh.description = "Average Relative Humidity for the day"

    rsds = nc.createVariable(
        "srad", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    rsds.units = "W m-2"
    rsds.scale_factor = 0.01
    rsds.long_name = "surface_downwelling_shortwave_flux_in_air"
    rsds.standard_name = "surface_downwelling_shortwave_flux_in_air"
    rsds.coordinates = "lon lat"
    rsds.description = "Global Shortwave Irradiance"
    nc.close()


def dl(valid: datetime):
    """get the files"""
    for vname in ["tmax", "tmin", "prate", "dswsfc", "q2m", "t2"]:
        localfn = f"{vname}.grb2"
        if Path(localfn).exists():
            LOG.info("Skipping %s as it exists", localfn)
            continue
        uri = (
            f"https://noaa-cfs-pds.s3.amazonaws.com/cfs.{valid:%Y%m%d/%H}/"
            f"time_grib_01/{vname}.01.{valid:%Y%m%d%H}.daily.grb2"
        )
        LOG.info("fetching %s", uri)
        resp = exponential_backoff(requests.get, uri, timeout=60)
        if resp is None or resp.status_code != 200:
            LOG.warning("Aborting as dl %s failed", uri)
            sys.exit(1)
        with open(localfn, "wb") as f:
            f.write(resp.content)


@click.command()
@click.option(
    "--date", "valid", type=click.DateTime(), help="UTC date", required=True
)
def main(valid: datetime):
    """Do main"""
    now = utc(valid.year, valid.month, valid.day, 0)
    workdir = Path(f"/mesonet/tmp/cfs{now:%Y%m%d%H}")
    workdir.mkdir(exist_ok=True)
    os.chdir(workdir)
    dl(now)
    for domain in DOMAINS:
        create_netcdf(now, domain)
        with ncopen("iemre.nc", "a") as nc:
            process2iemre(nc, now, domain)
        mydir = "iemre" if domain == "conus" else f"iemre_{domain}"
        shutil.move("iemre.nc", f"/mesonet/data/{mydir}/cfs_current.nc")

    # If we made it this far, we can blow out the tmp directory!
    os.chdir("/")
    shutil.rmtree(workdir)


if __name__ == "__main__":
    main()
