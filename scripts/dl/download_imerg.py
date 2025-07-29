"""Fetch NASA GPM data.

IMERG-Early has at most 4 hour latency.

IMERG-Late has about 14 hours.

Replace HHE with HHL

IMERG-Final is many months delayed

Drop L in the above.

2001-today

RUN from RUN_20AFTER.sh for 5 hours ago.
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import click
import httpx
import numpy as np
import rasterio
from PIL import Image
from pyiem import mrms
from pyiem.reference import ISO8601
from pyiem.util import logger, ncopen, utc

LOG = logger()


def get_geotiff(valid: datetime, source: str) -> np.ndarray | None:
    """Do the GeoTIFF workflow."""
    endts = valid + timedelta(minutes=29, seconds=59)
    minutes = valid.hour * 60 + valid.minute
    pp = "early" if source == "E" else f"{valid:%Y/%m}"
    url = (
        f"https://jsimpsonhttps.pps.eosdis.nasa.gov/imerg/gis/{pp}/"
        f"3B-HHR-{source}.MS.MRG.3IMERG.{valid:%Y%m%d}-S{valid:%H%M%S}-"
        f"E{endts:%H%M%S}.{minutes:04.0f}.V07B.30min.tif"
    )
    auth = httpx.NetRCAuth()
    with httpx.Client(auth=auth, follow_redirects=False) as client:
        LOG.info("Fetching %s", url)
        try:
            resp = client.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as exp:
            LOG.info("Error fetching %s: %s", url, exp)
            return None
        with open("pps.tif", "wb") as f:
            f.write(resp.content)
        with rasterio.open("pps.tif") as src:
            pmm = src.read(1) / 10.0
            # Life choice, set anything above 300mm to zero
            pmm = np.where(pmm > 300, 0, pmm)
    return pmm


def get_netcdf(valid, source) -> np.ndarray | None:
    """The NetCDF workflow"""
    url = valid.strftime(
        "https://gpm1.gesdisc.eosdis.nasa.gov/thredds/ncss/grid/aggregation/"
        f"GPM_3IMERGHH{source}.07/%Y/GPM_3IMERGHH{source}"
        ".07_Aggregation_%Y%03j.ncml.ncml?"
        "var=precipitation&time=%Y-%m-%dT%H%%3A%M%%3A00Z&"
        "accept=netcdf4-classic"
    )
    auth = httpx.NetRCAuth()
    with httpx.Client(auth=auth, follow_redirects=False) as client:
        resp = client.get(url, timeout=10)
        if resp.status_code in (301, 302, 303, 307, 308):
            url = resp.headers["Location"]
            LOG.info("Redirected to %s", url)
            resp = client.get(url, timeout=120, follow_redirects=True)
            if resp.status_code in (400, 404):  # Out of time bounds or no data
                LOG.info("Got %d, no data for %s", resp.status_code, valid)
                return None
        resp.raise_for_status()
    # Check content-type return header
    ct = resp.headers.get("content-type", "")
    if not ct.startswith("application/x-netcdf"):
        LOG.warning("Unexpected content-type for %s: %s", url, ct)
        return None
    with open("imerg.nc", "wb") as tmp:
        tmp.write(resp.content)
    with ncopen("imerg.nc") as nc:
        # x, y
        pmm = nc.variables["precipitation"][0, :, :] / 2.0  # mmhr to 30min
        pmm = np.flipud(pmm)
    return pmm


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC Valid Time")
@click.option("--realtime", is_flag=True, default=False)
def main(valid: datetime, realtime: bool):
    """Go Main Go."""
    valid = valid.replace(tzinfo=timezone.utc)
    routes = "ac" if realtime else "a"
    # If we are within 30 days of the valid time
    if (utc() - valid).total_seconds() < (3_600 * 24 * 30):
        for source in ("L", "E"):
            pmm = get_geotiff(valid, source)
            if pmm is not None:
                break
    else:
        pmm = get_netcdf(valid, "")
    if pmm is None:
        LOG.warning("No data for %s", valid)
        return

    if np.max(pmm) > 102:
        LOG.warning("overflow with max(%s) value > 102", np.max(pmm))
    # idx: 0-200 0.25mm  -> 50 mm
    # idx: 201-253 1mm -> 50-102 mm
    img = np.where(pmm >= 102, 254, 0)
    img = np.where(
        np.logical_and(pmm >= 50, pmm < 102),
        201 + (pmm - 50) / 1.0,
        img,
    )
    img = np.where(np.logical_and(pmm > 0, pmm < 50), pmm / 0.25, img)
    img = np.where(pmm < 0, 255, img)

    png = Image.fromarray(img.astype("u1"))
    png.putpalette(mrms.make_colorramp())
    png.save("imerg.png")

    metadata = {
        "start_valid": (valid - timedelta(minutes=15)).strftime(ISO8601),
        "end_valid": (valid + timedelta(minutes=15)).strftime(ISO8601),
        "units": "mm",
        "source": "F" if source == "" else source,  # E, L, F
        "generation_time": utc().strftime(ISO8601),
    }
    with open("imerg.json", "w", encoding="utf8") as fp:
        json.dump(metadata, fp)
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/imerg/p30m.json "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.json json",
        "imerg.json",
    ]
    subprocess.call(cmd)

    with open("imerg.wld", "w", encoding="utf8") as fp:
        fp.write("0.1\n0.0\n0.0\n-0.1\n-179.95\n89.95")
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/imerg/p30m.wld "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.wld wld",
        "imerg.wld",
    ]
    subprocess.call(cmd)

    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/imerg/p30m.png "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.png png",
        "imerg.png",
    ]
    subprocess.call(cmd)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as _tmpdir:
        os.chdir(_tmpdir)
        main()
