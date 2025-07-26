"""
Use the DWD ICON model to estimate IEMRE hourly fields for non CONUS domains.

https://www.dwd.de/DE/leistungen/opendata/help/modelle/Opendata_cdo_EN.pdf
https://www.dwd.de/DWD/forschung/nwv/fepub/icon_database_main.pdf

Called from RUN_40_AFTER.sh
 - top of next hour.
 - for something 12 hours ago, so to get closer radiation source

"""

import os
import subprocess
from datetime import datetime, timedelta, timezone

import click
import httpx
import numpy as np
import pygrib
from affine import Affine
from pyiem.iemre import (
    DOMAINS,
    get_hourly_ncname,
    hourly_offset,
    reproject2iemre,
)
from pyiem.util import logger, ncopen

LOG = logger()
META = {
    "skyc": {"gname": "clct"},
    "tmpk": {"gname": "t_2m"},
    "dwpk": {"gname": "td_2m"},
    "uwnd": {"gname": "u_10m"},
    "vwnd": {"gname": "v_10m"},
    "p01m": {"gname": "tot_prec"},
    "p01m_prev": {"gname": "tot_prec", "offset": 1},
    # Inconsistent on server, punted "soil4t": {"gname": "t_so"},
    # This is net shortwave
    "rsds": {"gname": "asob_s"},
    "rsds_prev": {"gname": "asob_s", "offset": 1},
}


def compute_model_valid(valid: datetime) -> datetime | None:
    """
    Compute the model valid time based on the provided valid datetime.
    The ICON model data is available at 00, 06, 12, and 18 UTC.
    """
    # We have to avoid F000 as precip and solar do not exist
    for offset in range(1, 24):
        model_valid = valid - timedelta(hours=offset)
        if model_valid.hour % 6 != 0:
            continue
        testfn = (
            f"https://opendata.dwd.de/weather/nwp/icon/grib/{model_valid:%H}/"
            f"t_2m/icon_global_icosahedral_single-level_{model_valid:%Y%m%d%H}_"
            f"{offset:03.0f}_T_2M.grib2.bz2"
        )
        try:
            with httpx.Client() as client:
                response = client.head(testfn)
            if response.status_code == 200:
                LOG.info("Found ICON model data for %s", model_valid)
                return model_valid
        except httpx.RequestError:
            # Handle request errors (e.g., network issues)
            continue
    return None


def grib_download(model_valid: datetime, valid: datetime) -> None:
    """
    Download the necessary GRIB files for the ICON model.
    """
    baseurl = (
        f"https://opendata.dwd.de/weather/nwp/icon/grib/{model_valid:%H}/"
    )
    fhour = (valid - model_valid).total_seconds() // 3600
    for var, meta in META.items():
        filename = f"{var}.grib2.bz2"
        if os.path.exists(filename):
            LOG.info("File %s already exists, skipping download", filename)
            continue
        fhour_off = fhour - meta.get("offset", 0)
        url = (
            f"{baseurl}{meta['gname']}/icon_global_icosahedral_single-level_"
            f"{model_valid:%Y%m%d%H}_{fhour_off:03.0f}_{meta['gname'].upper()}"
            ".grib2.bz2"
        )
        LOG.info("Downloading %s", url)
        try:
            with httpx.Client() as client:
                response = client.get(url)
            response.raise_for_status()
            with open(filename, "wb") as f:
                f.write(response.content)
            subprocess.run(["bzip2", "-d", filename], check=True)
            # Use cdo to convert grid to lat/lon
            with subprocess.Popen(
                [
                    "cdo",
                    "-f",
                    "grb2",
                    (
                        "remap,/mesonet/data/meta/icon_description.txt,"
                        "/mesonet/data/meta/icon_weights.nc"
                    ),
                    f"{var}.grib2",
                    f"{var}_latlon.grib2",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as proc:
                stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                LOG.error(
                    "CDO remap failed for %s: %s %s",
                    filename,
                    stderr.decode("utf-8"),
                    stdout.decode("utf-8"),
                )
        except httpx.RequestError as e:
            LOG.error("Failed to download %s: %s", filename, e)


def copy_grib_to_netcdf(valid: datetime, domain: str, fhour: int) -> None:
    """Fun times."""
    idx = hourly_offset(valid)
    # grib file is stored S to N
    affine_in = Affine(0.125, 0, -180.0, 0, 0.125, -90.0)
    with ncopen(get_hourly_ncname(valid.year, domain), "a") as nc:
        for var in META:
            if var.endswith("_prev"):  # lame
                continue
            grib_file = f"{var}_latlon.grib2"
            if not os.path.exists(grib_file):
                LOG.warning("GRIB file %s does not exist, skipping", grib_file)
                continue
            with pygrib.open(grib_file) as grbs:
                values = grbs[1].values
            if var == "p01m":
                with pygrib.open(f"{var}_prev_latlon.grib2") as grbs:
                    values = values - grbs[1].values
            if var == "rsds":
                with pygrib.open(f"{var}_prev_latlon.grib2") as grbs:
                    values = (values * fhour) - (grbs[1].values * (fhour - 1))
            iemre_data = reproject2iemre(
                values, affine_in, "EPSG:4326", domain=domain
            )
            LOG.info(
                "Write %s[%s]@%s mean: %.2f",
                var,
                domain,
                idx,
                np.mean(iemre_data),
            )
            nc.variables[var][idx] = iemre_data


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
@click.option("--keep", is_flag=True, help="Keep temporary files")
def main(valid: datetime, keep: bool) -> None:
    """Main function to process ICON data for IEMRE."""
    valid = valid.replace(tzinfo=timezone.utc)
    # 1. Figure out which ICON model is available for usage
    model_valid = compute_model_valid(valid)
    if model_valid is None:
        LOG.warning("No ICON model data available for %s", valid)
        return
    # 2. Download the necessary files
    tmpdir = f"/mesonet/tmp/icon{valid:%Y%m%d%H}"
    os.makedirs(tmpdir, exist_ok=True)
    os.chdir(tmpdir)
    grib_download(model_valid, valid)
    fhour = (valid - model_valid).total_seconds() // 3600
    # 3. Copy to IEMRE netcdf files
    for domain in DOMAINS:
        if domain == "":
            continue
        copy_grib_to_netcdf(valid, domain, fhour)
    # 4. Cleanup
    os.chdir("/mesonet/tmp")
    if not keep:
        LOG.info("Cleaning up temporary files in %s", tmpdir)
        subprocess.run(["rm", "-rf", tmpdir], check=True)


if __name__ == "__main__":
    main()
