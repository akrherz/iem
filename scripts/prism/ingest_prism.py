"""Ingest the PRISM data into a local yearly netCDF file

RUN_2AM.sh for 7,60,365 days ago
RUN_NOON.sh for 1 day ago
"""

import glob
import os
import subprocess
import warnings
from datetime import datetime

import click
import httpx
import numpy as np
import rasterio
from pyiem.iemre import daily_offset
from pyiem.util import get_properties, logger, ncopen, set_property

# unavoidable warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=".*?invalid value encountered in cast.*?",
)

LOG = logger()
PROPNAME = "prism.archive_end"


def process(valid: datetime):
    """Make the download happen!"""
    idx = daily_offset(valid)
    for varname in ["ppt", "tmax", "tmin"]:
        uri = (
            f"https://services.nacse.org/prism/data/get/us/800m/{varname}/"
            f"{valid:%Y%m%d}"
        )
        try:
            resp = httpx.get(uri, timeout=120)
            resp.raise_for_status()
            with open(f"{valid:%Y%m%d}.zip", "wb") as fh:
                fh.write(resp.content)
            subprocess.call(
                [
                    "unzip",
                    "-q",
                    f"{valid:%Y%m%d}.zip",
                ]
            )
            os.remove(f"{valid:%Y%m%d}.zip")
        except Exception as exp:
            LOG.error("Failed to download %s: %s", uri, exp)
            continue
        tifffn = f"prism_{varname}_us_30s_{valid:%Y%m%d}.tif"
        with rasterio.open(tifffn) as src:
            # raster is top down, netcdf is bottom up
            data = np.flipud(src.read(1))
            # values of -9999 are nodata
            data = np.ma.masked_array(
                data, mask=(data < -9000), fill_value=np.nan
            )
            LOG.info(
                "%s min: %s max: %s", varname, np.nanmin(data), np.nanmax(data)
            )
        with ncopen(f"/mesonet/data/prism/{valid:%Y}_daily.nc", "a") as nc:
            nc.variables[varname][idx] = data
        for fn in glob.glob(f"prism_{varname}_us_30s_{valid:%Y%m%d}*"):
            os.remove(fn)


def update_properties(valid):
    """Conditionally update the database flag for when PRISM ends."""
    props = get_properties()
    current = datetime.strptime(
        props.get(PROPNAME, "1980-01-01"),
        "%Y-%m-%d",
    ).date()
    if current > valid:
        return
    set_property(PROPNAME, valid.strftime("%Y-%m-%d"))


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), required=True, help="Date"
)
def main(dt: datetime):
    """Do Something"""
    os.chdir("/mesonet/tmp")
    dt = dt.date()
    process(dt)
    update_properties(dt)


if __name__ == "__main__":
    main()
