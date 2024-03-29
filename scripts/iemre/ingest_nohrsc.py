"""Ingest the NOHRSC snow analysis data into the IEMRE database."""

import os
import subprocess
import tempfile

import click
import httpx
from affine import Affine
from pyiem.iemre import get_grids, reproject2iemre, set_grids
from pyiem.util import logger, ncopen

LOG = logger()


@click.command()
@click.option("--date", "valid", type=click.DateTime(), help="Date to process")
def main(valid):
    """Verbatim copy to snow_12z"""
    url = valid.strftime(
        "https://www.nohrsc.noaa.gov/snowfall/data/%Y%m/"
        "sfav2_CONUS_24h_%Y%m%d12.nc"
    )
    with httpx.Client() as client:
        req = client.get(url)
        if req.status_code != 200:
            LOG.warning("%s got status code %s", url, req.status_code)
            return
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(req.content)
    with ncopen(tmp.name) as nc:
        lats = nc.variables["lat"][:]
        lons = nc.variables["lon"][:]
        snow = nc.variables["Data"][:] * 1_000.0  # m to mm
    aff_in = Affine(
        lons[1] - lons[0], 0.0, lons[0], 0.0, lats[1] - lats[0], lats[0]
    )
    snow12z = reproject2iemre(snow, aff_in, "EPSG:4326")
    ds = get_grids(valid.date(), varnames=["snow_12z"])
    ds.variables["snow_12z"][:] = snow12z
    set_grids(valid.date(), ds)
    subprocess.call(
        [
            "python",
            "db_to_netcdf.py",
            f"{valid:%Y}",
            f"{valid:%m}",
            f"{valid:%d}",
        ]
    )

    os.unlink(tmp.name)


if __name__ == "__main__":
    main()
