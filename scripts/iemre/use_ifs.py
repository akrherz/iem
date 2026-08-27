"""
Open-Meteo makes the 1 hour IFS output available on AWS.

https://openmeteo.s3.amazonaws.com/index.html#data_spatial/ecmwf_ifs

For non-CONUS IEMRE domains, this is the "observation" database prior to the
arrival of ERA5Land.  For all IEMRE domains, this is "the forecast"

Called from RUN_40_AFTER.sh (4x per day)

  - Since there are only 4x runs per day and we are forward filling IEMRE
    hourly grids, we just need to run 4x per day.

"""

import os
import tempfile
from datetime import datetime, timedelta, timezone

import click
import requests
from affine import Affine
from earthkit.regrid import interpolate
from metpy.units import units
from omfiles import OmFileReader
from pyiem.iemre import (
    DOMAINS,
    get_hourly_ncname,
    hourly_offset,
    reproject2iemre,
)
from pyiem.util import logger, ncopen, utc

LOG = logger()
# https://www.ecmwf.int/en/forecasts/datasets/open-data
META = {}
IFS_HAS_HOURS = 90
XREF = {
    "tmpc": "temperature_2m",
    "soilc": "soil_temperature_0_to_7cm",
    "uwnd": "wind_u_component_10m",
    "vwnd": "wind_v_component_10m",
    "dwpc": "dew_point_2m",
    "cloud_cover": "cloud_cover",
    "swdn": "shortwave_radiation",
    "precip": "precipitation",
}


def compute_model_valid(valid: datetime) -> datetime | None:
    """
    Compute the model valid time based on the provided valid datetime.
    """
    # We have to avoid F000 as precip and solar do not exist
    for offset in range(1, 24):
        model_valid = valid - timedelta(hours=offset)
        if model_valid.hour % 6 != 0:
            continue
        testfn = (
            "https://openmeteo.s3.amazonaws.com/data_spatial/"
            f"ecmwf_ifs/{model_valid:%Y/%m/%d/%H%M}Z/"
            f"{valid:%Y-%m-%dT%H%M}.om"
        )
        LOG.info("Checking for %s", testfn)
        try:
            with requests.Session() as client:
                response = client.head(testfn)
            if response.status_code == 200:
                LOG.info("Found IFS model data for %s", model_valid)
                return model_valid
        except requests.RequestException:
            # Handle request errors (e.g., network issues)
            continue
    return None


def process_omfile(root: OmFileReader, valid: datetime, tidx: int) -> None:
    """Process the Open-Meteo IFS file."""
    affine = Affine(
        0.125,
        0.0,
        0.0,
        0.0,
        -0.125,
        90.0,
    )
    # Print out the inventory
    for omidx in range(root.num_children):
        child = root.get_child_by_index(omidx)
        LOG.debug("Child %s: %s", omidx, child.name)
    ncvars = {}
    for ncvar, omname in XREF.items():
        # Believe this goes 0-360 lon and 90 to -90 lat
        ncvars[ncvar] = interpolate(
            root.get_child_by_name(omname)[:],
            in_grid={"grid": "O1280"},
            out_grid={"grid": [0.125, 0.125]},
            method="linear",
        )

    for domain in DOMAINS:
        # We only allow this for the CONUS domain when it is in the future
        # In theory, this should never happen, but perhaps dl gets slow
        if domain in ("", "conus") and valid < utc():
            LOG.warning("Not allowing %s to overwrite IEMRE CONUS", valid)
            continue
        with ncopen(
            get_hourly_ncname(valid.year, domain), "a", timeout=600
        ) as nc:
            # No unit conversions
            for ncvar, omvar in [
                ("uwnd", ncvars["uwnd"]),
                ("vwnd", ncvars["vwnd"]),
                ("skyc", ncvars["cloud_cover"]),
                ("rsds", ncvars["swdn"]),
                ("p01m", ncvars["precip"]),
            ]:
                nc.variables[ncvar][tidx] = reproject2iemre(
                    omvar[:],
                    affine,
                    "EPSG:4326",
                    domain=domain,
                )

            # C to K
            for ncvar, omvar in [
                ("tmpk", ncvars["tmpc"]),
                ("dwpk", ncvars["dwpc"]),
                ("soil4t", ncvars["soilc"]),
            ]:
                nc.variables[ncvar][tidx] = (
                    (
                        units.degC
                        * reproject2iemre(
                            omvar[:],
                            affine,
                            "EPSG:4326",
                            domain=domain,
                        )
                    )
                    .to(units.degK)
                    .m
                )


def process(valid: datetime, model_valid: datetime) -> None:
    """Fun times."""
    tidx = hourly_offset(valid)
    LOG.info("Processing %s from %s run at tidx: %s", valid, model_valid, tidx)

    filename = f"{valid:%Y-%m-%dT%H%M}.om"
    if not os.path.isfile(filename):
        uri = (
            "https://openmeteo.s3.amazonaws.com/data_spatial/ecmwf_ifs/"
            f"{model_valid:%Y/%m/%d/%H%M}Z/{filename}"
        )
        LOG.info("Downloading %s", uri)
        with requests.get(uri, stream=True, timeout=120.0) as response:
            response.raise_for_status()
            with open(filename, "wb") as fh:
                fh.writelines(response.iter_content(chunk_size=64 * 1024))

    with OmFileReader(filename) as root:
        process_omfile(root, valid, tidx)
    os.unlink(filename)


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
def main(valid: datetime) -> None:
    """Main function to process IFS data for IEMRE."""
    valid = valid.replace(tzinfo=timezone.utc)
    # 1. Figure out which IFS model is available for usage
    model_valid = compute_model_valid(valid)
    if model_valid is None:
        LOG.warning("No IFS model data available for %s", valid)
        return
    fhour = int((valid - model_valid).total_seconds() / 3600)
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        while fhour <= IFS_HAS_HOURS:
            # 3. Process
            process(model_valid + timedelta(hours=fhour), model_valid)
            fhour += 1


if __name__ == "__main__":
    main()
