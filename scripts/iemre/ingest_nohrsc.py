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
    try:
        resp = httpx.get(url, timeout=60)
        resp.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(resp.content)
    except Exception as exp:
        LOG.warning("download failed: %s %s", url, exp)
        return
    with ncopen(tmp.name) as nc:
        lats = nc.variables["lat"][:]
        lons = nc.variables["lon"][:]
        snow = nc.variables["Data"][:] * 1_000.0  # m to mm
    dx = lons[1] - lons[0]
    dy = lats[1] - lats[0]
    # This is the SW edge, not the center
    aff_in = Affine(dx, 0.0, lons[0] - dx / 2.0, 0.0, dy, lats[0] - dy / 2.0)
    snow12z = reproject2iemre(snow, aff_in, "EPSG:4326")
    ds = get_grids(valid.date(), varnames=["snow_12z"])
    ds.variables["snow_12z"][:] = snow12z
    set_grids(valid.date(), ds)
    subprocess.call(
        [
            "python",
            "db_to_netcdf.py",
            f"--date={valid:%Y-%m-%d}",
            "--varname=snow_12z",
            "--domain=conus",
        ]
    )

    os.unlink(tmp.name)


if __name__ == "__main__":
    main()
