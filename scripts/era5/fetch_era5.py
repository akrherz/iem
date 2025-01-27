"""Download an hour worth of ERA5.

Run from RUN_0Z_ERA5LAND.sh for 5 days ago.
"""

import os
import subprocess
import sys
import tempfile
import warnings
from datetime import timedelta

import cdsapi
import click
import numpy as np
from netCDF4 import Dataset
from pyiem.grid.nav import get_nav
from pyiem.iemre import hourly_offset
from pyiem.util import logger, ncopen, utc

LOG = logger()
CDSVARS = (
    "10m_u_component_of_wind 10m_v_component_of_wind 2m_dewpoint_temperature "
    "2m_temperature soil_temperature_level_1 soil_temperature_level_2 "
    "soil_temperature_level_3 soil_temperature_level_4 "
    "surface_solar_radiation_downwards total_evaporation total_precipitation "
    "volumetric_soil_water_layer_1 volumetric_soil_water_layer_2 "
    "volumetric_soil_water_layer_3 volumetric_soil_water_layer_4"
).split()
VERBATIM = {
    "u10": "uwnd",
    "v10": "vwnd",
    "d2m": "dwpk",
    "t2m": "tmpk",
}
# unavoidable
warnings.simplefilter("ignore", RuntimeWarning)


def ingest(ncin: Dataset, nc: Dataset, valid, domain):
    """Consume this grib file."""
    tidx = hourly_offset(valid)
    dd = "" if domain == "" else f"_{domain}"

    for ekey, key in VERBATIM.items():
        nc.variables[key][tidx] = np.flipud(ncin.variables[ekey][0])

    nc.variables["soilt"][tidx, 0] = np.flipud(ncin.variables["stl1"][0])
    nc.variables["soilt"][tidx, 1] = np.flipud(ncin.variables["stl2"][0])
    nc.variables["soilt"][tidx, 2] = np.flipud(ncin.variables["stl3"][0])
    nc.variables["soilt"][tidx, 3] = np.flipud(ncin.variables["stl4"][0])

    nc.variables["soilm"][tidx, 0] = np.flipud(ncin.variables["swvl1"][0])
    nc.variables["soilm"][tidx, 1] = np.flipud(ncin.variables["swvl2"][0])
    nc.variables["soilm"][tidx, 2] = np.flipud(ncin.variables["swvl3"][0])
    nc.variables["soilm"][tidx, 3] = np.flipud(ncin.variables["swvl4"][0])

    # -- these vars are accumulated since 0z, so 0z is the 24hr sum
    rsds = nc.variables["rsds"]
    p01m = nc.variables["p01m"]
    evap = nc.variables["evap"]
    if valid.hour == 0:
        tidx0 = hourly_offset(valid - timedelta(hours=24))
        # Special 1 Jan consideration
        if valid.month == 1 and valid.day == 1 and valid.year > 1950:
            with ncopen(
                f"/mesonet/data/era5{dd}/{valid.year - 1}_era5land_hourly.nc"
            ) as nc2:
                tsolar = np.sum(nc2.variables["rsds"][(tidx0 + 1)], 0) * 3600.0
                tp01m = np.sum(nc2.variables["p01m"][(tidx0 + 1)], 0)
                tevap = np.sum(nc2.variables["evap"][(tidx0 + 1)], 0)
        else:
            tsolar = np.sum(rsds[(tidx0 + 1) : tidx], 0) * 3600.0
            tp01m = np.sum(p01m[(tidx0 + 1) : tidx], 0)
            tevap = np.sum(evap[(tidx0 + 1) : tidx], 0)
    elif valid.hour > 1:
        tidx0 = hourly_offset(valid.replace(hour=1))
        tsolar = np.sum(rsds[tidx0:tidx], 0) * 3600.0
        tp01m = np.sum(p01m[tidx0:tidx], 0)
        tevap = np.sum(evap[tidx0:tidx], 0)
    else:
        tsolar = np.zeros(ncin.variables["t2m"][0].shape)
        tp01m = np.zeros(ncin.variables["t2m"][0].shape)
        tevap = np.zeros(ncin.variables["t2m"][0].shape)
    # J m-2 to W/m2
    val = np.flipud(ncin.variables["ssrd"][0])
    newval = (val - tsolar) / 3600.0
    # Le Sigh, sometimes things are negative, somehow?
    rsds[tidx] = np.ma.where(newval < 0, 0, newval)
    # m to mm
    val = np.flipud(ncin.variables["e"][0])
    newval = (val * 1000.0) - tevap
    evap[tidx] = np.ma.where(newval < 0, 0, newval)
    # m to mm
    val = np.flipud(ncin.variables["tp"][0])
    newval = (val * 1000.0) - tp01m
    p01m[tidx] = np.ma.where(newval < 0, 0, newval)


def run(valid, domain: str, force):
    """Run for the given valid time."""
    dd = "" if domain == "" else f"_{domain}"
    ncoutfn = f"/mesonet/data/era5{dd}/{valid.year}_era5land_hourly.nc"
    tidx = hourly_offset(valid)
    if not force:
        with ncopen(ncoutfn) as nc:
            sample = nc.variables["tmpk"][tidx, 150, 150]
            if 200 < sample < 350:
                LOG.info(
                    "Skipping %s, tmpk %.1fK for domain `%s`",
                    valid,
                    sample,
                    domain,
                )
                return
    gridnav = get_nav("era5land", domain)
    LOG.info("Running for %s[domain=%s]", valid, domain)
    zipfn = f"{domain}_{valid:%Y%m%d%H}.zip"

    cds = cdsapi.Client(quiet=True, progress=sys.stdout.isatty())

    cds.retrieve(
        "reanalysis-era5-land",
        {
            "variable": CDSVARS,
            "year": f"{valid.year}",
            "month": f"{valid:%m}",
            "day": [f"{valid:%d}"],
            "time": [f"{valid:%H}:00"],
            # Unclear what is happening here, but the download seems to
            # conform to the requested grid
            "area": [
                gridnav.top,
                gridnav.left,
                gridnav.bottom,
                gridnav.right,
            ],
            "data_format": "netcdf",
            "download_format": "zip",
        },
        zipfn,
    )
    # unzip
    subprocess.call(["unzip", "-q", zipfn])
    os.unlink(zipfn)
    with ncopen("data_0.nc") as ncin, ncopen(ncoutfn, "a") as nc:
        ingest(ncin, nc, valid, domain)
    os.unlink("data_0.nc")


@click.command()
@click.option("--date", "valid", required=True, type=click.DateTime())
@click.option("--domain", default=None, help="IEMRE Domain to run for")
@click.option("--force", is_flag=True, help="Force re-download")
def main(valid, domain, force: bool):
    """Go!"""
    valid = utc(valid.year, valid.month, valid.day)
    domains = ["", "china", "europe"]
    if domain is not None:
        domains = [domain]
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        for offset in range(1, 25):
            for _domain in domains:
                run(valid + timedelta(hours=offset), _domain, force)


if __name__ == "__main__":
    main()
