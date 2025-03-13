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
from pyiem.util import exponential_backoff, logger, ncopen, utc

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
        "https://gpm1.gesdisc.eosdis.nasa.gov/thredds/ncss/aggregation/"
        f"GPM_3IMERGHH{source}.06/%Y/GPM_3IMERGHH{source}"
        ".06_Aggregation_%Y%03j.ncml.ncml?"
        "var=precipitationCal&time=%Y-%m-%dT%H%%3A%M%%3A00Z&accept=netcdf4"
    )
    req = exponential_backoff(httpx.get, url, timeout=120)
    if req is None:
        LOG.warning("Unable to get %s", url)
        return
    ct = req.headers.get("content-type", "")
    # Sometimes, the service returns a 200 that is an error webpage :(
    if req.status_code != 200 or not ct.startswith("application/x-netcdf4"):
        LOG.info(
            "failed to fetch %s [%s, %s] using source %s",
            valid,
            req.status_code,
            ct,
            source,
        )
        LOG.info(url)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(req.content)
    with ncopen(tmp.name) as nc:
        # x, y
        pmm = nc.variables["precipitationCal"][0, :, :] / 2.0  # mmhr to 30min
        pmm = np.flipud(pmm.T)
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
