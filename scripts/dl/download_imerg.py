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
from PIL import Image
from pyiem import mrms
from pyiem.reference import ISO8601
from pyiem.util import logger, ncopen, utc

LOG = logger()


def compute_source(valid):
    """Which source to use."""
    utcnow = utc()
    if (utcnow - valid) < timedelta(hours=24):
        return "E"
    if (utcnow - valid) < timedelta(days=120):
        return "L"
    return ""


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC Valid Time")
@click.option("--realtime", is_flag=True, default=False)
def main(valid: datetime, realtime: bool):
    """Go Main Go."""
    valid = valid.replace(tzinfo=timezone.utc)
    source = compute_source(valid)
    routes = "ac" if realtime else "a"
    LOG.info("Using source: `%s` for valid: %s[%s]", source, valid, routes)
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
                return
        resp.raise_for_status()
    # Check content-type return header
    ct = resp.headers.get("content-type", "")
    if not ct.startswith("application/x-netcdf"):
        LOG.warning("Unexpected content-type for %s: %s", url, ct)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(resp.content)
    with ncopen(tmp.name) as nc:
        # x, y
        pmm = nc.variables["precipitation"][0, :, :] / 2.0  # mmhr to 30min
        pmm = np.flipud(pmm)
    os.unlink(tmp.name)

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
    png.save(f"{tmp.name}.png")

    metadata = {
        "start_valid": (valid - timedelta(minutes=15)).strftime(ISO8601),
        "end_valid": (valid + timedelta(minutes=15)).strftime(ISO8601),
        "units": "mm",
        "source": "F" if source == "" else source,  # E, L, F
        "generation_time": utc().strftime(ISO8601),
    }
    with open(f"{tmp.name}.json", "w", encoding="utf8") as fp:
        json.dump(metadata, fp)
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/imerg/p30m.json "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.json json",
        f"{tmp.name}.json",
    ]
    subprocess.call(cmd)
    os.unlink(f"{tmp.name}.json")

    with open(f"{tmp.name}.wld", "w", encoding="utf8") as fp:
        fp.write("0.1\n0.0\n0.0\n-0.1\n-179.95\n89.95")
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/imerg/p30m.wld "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.wld wld",
        f"{tmp.name}.wld",
    ]
    subprocess.call(cmd)
    os.unlink(f"{tmp.name}.wld")

    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"plot {routes} {valid:%Y%m%d%H%M} gis/images/4326/imerg/p30m.png "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.png png",
        f"{tmp.name}.png",
    ]
    subprocess.call(cmd)
    os.unlink(f"{tmp.name}.png")


if __name__ == "__main__":
    main()
