"""Download an hour worth of ERA5.

Run from RUN_0Z_ERA5LAND.sh for 5 days ago.
"""

import os
import subprocess
import sys
import tempfile
import warnings
from datetime import datetime, timedelta

import cdsapi
import click
import numpy as np
from netCDF4 import Dataset
from pyiem.iemre import DOMAINS, hourly_offset
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
    # The grid delta and grid points are hopefully the same, we just need to
    # figure out where they are.
    # ncin is also top/down sigh.  90 to -90 , 0 to 359.9
    lon = nc.variables["lon"][0]
    if lon < 0:
        lon += 360.0  # convert to match in
    lat = nc.variables["lat"][0]
    delta = 0.1
    # Find the grid points
    ll_j = int((90 - lat) / delta)
    ul_j = ll_j - nc.dimensions["lat"].size
    jslice = slice(ul_j, ll_j)
    ll_i = int(lon / delta)
    ur_i = ll_i + nc.dimensions["lon"].size
    islice = slice(ll_i, ur_i)

    # Of course, our Europe domain crosses the 0/360 boundary, so we have
    # pain here
    islices = [islice]
    islices_out = [slice(None, None)]
    if domain == "europe":
        # NCIN starts at 0 and ends at 359.9
        lon2 = nc.variables["lon"][-1]
        # plus 2 since we include zero and the end cell
        islices = [slice(ll_i, 3599), slice(0, int(lon2 / delta) + 1)]
        i0 = islices[0].stop - islices[0].start
        islices_out = [slice(0, i0), slice(i0 + 1, None)]

    LOG.debug(
        "domain: %s islices[%s]: %s jslice[%s]: %s",
        domain,
        lon,
        islices,
        lat,
        jslice,
    )

    tidx = hourly_offset(valid)
    dd = "" if domain == "" else f"_{domain}"

    for islice_in, islice_out in zip(islices, islices_out, strict=False):
        for ekey, key in VERBATIM.items():
            nc.variables[key][tidx, :, islice_out] = np.flipud(
                ncin.variables[ekey][0, jslice, islice_in]
            )

        nc.variables["soilt"][tidx, 0, :, islice_out] = np.flipud(
            ncin.variables["stl1"][0, jslice, islice_in]
        )
        nc.variables["soilt"][tidx, 1, :, islice_out] = np.flipud(
            ncin.variables["stl2"][0, jslice, islice_in]
        )
        nc.variables["soilt"][tidx, 2, :, islice_out] = np.flipud(
            ncin.variables["stl3"][0, jslice, islice_in]
        )
        nc.variables["soilt"][tidx, 3, :, islice_out] = np.flipud(
            ncin.variables["stl4"][0, jslice, islice_in]
        )

        nc.variables["soilm"][tidx, 0, :, islice_out] = np.flipud(
            ncin.variables["swvl1"][0, jslice, islice_in]
        )
        nc.variables["soilm"][tidx, 1, :, islice_out] = np.flipud(
            ncin.variables["swvl2"][0, jslice, islice_in]
        )
        nc.variables["soilm"][tidx, 2, :, islice_out] = np.flipud(
            ncin.variables["swvl3"][0, jslice, islice_in]
        )
        nc.variables["soilm"][tidx, 3, :, islice_out] = np.flipud(
            ncin.variables["swvl4"][0, jslice, islice_in]
        )

        # -- these vars are accumulated since 0z, so 0z is the 24hr sum
        rsds = nc.variables["rsds"]
        p01m = nc.variables["p01m"]
        evap = nc.variables["evap"]
        if valid.hour == 0:
            tidx0 = hourly_offset(valid - timedelta(hours=24))
            # Special 1 Jan consideration
            if valid.month == 1 and valid.day == 1 and valid.year > 1950:
                with ncopen(
                    f"/mesonet/data/era5{dd}/"
                    f"{valid.year - 1}_era5land_hourly.nc"
                ) as nc2:
                    tsolar = (
                        np.sum(
                            nc2.variables["rsds"][(tidx0 + 1), :, islice_out],
                            0,
                        )
                        * 3600.0
                    )
                    tp01m = np.sum(
                        nc2.variables["p01m"][(tidx0 + 1), :, islice_out], 0
                    )
                    tevap = np.sum(
                        nc2.variables["evap"][(tidx0 + 1), :, islice_out], 0
                    )
            else:
                tsolar = (
                    np.sum(rsds[(tidx0 + 1) : tidx, :, islice_out], 0) * 3600.0
                )
                tp01m = np.sum(p01m[(tidx0 + 1) : tidx, :, islice_out], 0)
                tevap = np.sum(evap[(tidx0 + 1) : tidx, :, islice_out], 0)
        elif valid.hour > 1:
            tidx0 = hourly_offset(valid.replace(hour=1))
            tsolar = np.sum(rsds[tidx0:tidx, :, islice_out], 0) * 3600.0
            tp01m = np.sum(p01m[tidx0:tidx, :, islice_out], 0)
            tevap = np.sum(evap[tidx0:tidx, :, islice_out], 0)
        else:
            tsolar = np.zeros(
                ncin.variables["t2m"][0, jslice, islice_in].shape
            )
            tp01m = np.zeros(ncin.variables["t2m"][0, jslice, islice_in].shape)
            tevap = np.zeros(ncin.variables["t2m"][0, jslice, islice_in].shape)
        # J m-2 to W/m2
        val = np.flipud(ncin.variables["ssrd"][0, jslice, islice_in])
        newval = (val - tsolar) / 3600.0
        # Le Sigh, sometimes things are negative, somehow?
        rsds[tidx, :, islice_out] = np.ma.where(newval < 0, 0, newval)
        # m to mm
        val = np.flipud(ncin.variables["e"][0, jslice, islice_in])
        newval = (val * 1000.0) - tevap
        evap[tidx, :, islice_out] = np.ma.where(newval < 0, 0, newval)
        # m to mm
        val = np.flipud(ncin.variables["tp"][0, jslice, islice_in])
        newval = (val * 1000.0) - tp01m
        p01m[tidx, :, islice_out] = np.ma.where(newval < 0, 0, newval)


def fetch(valid: datetime, checkcache: bool):
    """Get the data from the CDS."""
    if checkcache:
        remotepath = (
            f"/mnt/era5land/{valid:%Y/%m}/era5land_{valid:%Y%m%d%H}.nc"
        )
        cmd = [
            "/usr/bin/scp",
            "-q",
            f"mesonet@metvm5-dc:{remotepath}",
            "data_0.nc",
        ]
        LOG.info("command `%s`", " ".join(cmd))
        subprocess.call(cmd)
        if os.path.isfile("data_0.nc"):
            LOG.info("Found %s in cache", remotepath)
            return

    zipfn = "data_0.nc.zip"
    cds = cdsapi.Client(quiet=True, progress=sys.stdout.isatty())
    cds.retrieve(
        "reanalysis-era5-land",
        {
            "variable": CDSVARS,
            "year": f"{valid.year}",
            "month": f"{valid:%m}",
            "day": [f"{valid:%d}"],
            "time": [f"{valid:%H}:00"],
            "data_format": "netcdf",
            "download_format": "zip",
        },
        zipfn,
    )
    # unzip
    subprocess.call(["unzip", "-q", zipfn])
    os.unlink(zipfn)


def archive(fn: str, valid: datetime):
    """Copy file to the long term archive."""
    remotepath = f"/mnt/era5land/{valid:%Y/%m}"
    cmd = [
        "/usr/bin/rsync",
        "--rsync-path",
        f"mkdir -p {remotepath} && rsync",
        "-a",
        fn,
        f"mesonet@metvm5-dc:{remotepath}/era5land_{valid:%Y%m%d%H}.nc",
    ]
    LOG.info("command `%s`", " ".join(cmd))
    if subprocess.call(cmd) != 0:
        LOG.error("Failed to copy %s to remote", fn)


def run(valid: datetime, justdomain: str | None, checkcache: bool):
    """Run for the given valid time."""
    fetch(valid, checkcache)
    for domain in DOMAINS if justdomain is None else [justdomain]:
        dd = "" if domain == "" else f"_{domain}"
        ncoutfn = f"/mesonet/data/era5{dd}/{valid.year}_era5land_hourly.nc"
        LOG.info("Running for %s[domain=%s]", valid, domain)
        with ncopen("data_0.nc") as ncin, ncopen(ncoutfn, "a") as nc:
            ingest(ncin, nc, valid, domain)
    archive("data_0.nc", valid)
    os.unlink("data_0.nc")


@click.command()
@click.option("--date", "valid", required=True, type=click.DateTime())
@click.option("--domain")
@click.option("--checkcache", is_flag=True, default=False)
def main(valid: datetime, domain: str | None, checkcache: bool):
    """Go!"""
    valid = utc(valid.year, valid.month, valid.day)
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        for offset in range(1, 25):
            run(valid + timedelta(hours=offset), domain, checkcache)


if __name__ == "__main__":
    main()
