"""Fetch NASA GPM data.

IMERG-Early has at most 4 hour latency.


IMERG-Late has about 14 hours.

Replace HHE with HHL

IMERG-Final is many months delayed

Drop L in the above.

2001-today

RUN from RUN_20AFTER.sh for 5 hours ago.
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import requests
from PIL import Image
from pyiem import mrms
from pyiem.util import exponential_backoff, logger, ncopen, utc

LOG = logger()


def compute_source(valid):
    """Which source to use."""
    utcnow = utc()
    if (utcnow - valid) < datetime.timedelta(hours=24):
        return "E"
    if (utcnow - valid) < datetime.timedelta(days=120):
        return "L"
    return ""


def main(argv):
    """Go Main Go."""
    valid = utc(*[int(a) for a in argv[1:6]])
    source = compute_source(valid)
    routes = "ac" if len(argv) > 6 else "a"
    LOG.info("Using source: `%s` for valid: %s[%s]", source, valid, routes)
    url = valid.strftime(
        "https://gpm1.gesdisc.eosdis.nasa.gov/thredds/ncss/aggregation/"
        f"GPM_3IMERGHH{source}.06/%Y/GPM_3IMERGHH{source}"
        ".06_Aggregation_%Y%03j.ncml.ncml?"
        "var=precipitationCal&time=%Y-%m-%dT%H%%3A%M%%3A00Z&accept=netcdf4"
    )
    req = exponential_backoff(requests.get, url, timeout=120)
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

    ISO = "%Y-%m-%dT%H:%M:%SZ"
    metadata = {
        "start_valid": (valid - datetime.timedelta(minutes=15)).strftime(ISO),
        "end_valid": (valid + datetime.timedelta(minutes=15)).strftime(ISO),
        "units": "mm",
        "source": "F" if source == "" else source,  # E, L, F
        "generation_time": utc().strftime(ISO),
    }
    with open(f"{tmp.name}.json", "w", encoding="utf8") as fp:
        json.dump(metadata, fp)
    pqstr = (
        f"pqinsert -i -p 'plot {routes} {valid:%Y%m%d%H%M} "
        "gis/images/4326/imerg/p30m.json "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.json json' {tmp.name}.json"
    )
    subprocess.call(pqstr, shell=True)
    os.unlink(f"{tmp.name}.json")

    with open(f"{tmp.name}.wld", "w", encoding="utf8") as fp:
        fp.write("\n".join(["0.1", "0.0", "0.0", "-0.1", "-179.95", "89.95"]))
    pqstr = (
        f"pqinsert -i -p 'plot {routes} {valid:%Y%m%d%H%M} "
        "gis/images/4326/imerg/p30m.wld "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.wld wld' {tmp.name}.wld"
    )
    subprocess.call(pqstr, shell=True)
    os.unlink(f"{tmp.name}.wld")

    pqstr = (
        f"pqinsert -i -p 'plot {routes} {valid:%Y%m%d%H%M} "
        "gis/images/4326/imerg/p30m.png "
        f"GIS/imerg/p30m_{valid:%Y%m%d%H%M}.png png' {tmp.name}.png"
    )
    subprocess.call(pqstr, shell=True)
    os.unlink(f"{tmp.name}.png")


if __name__ == "__main__":
    main(sys.argv)
