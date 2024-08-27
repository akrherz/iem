"""
 Since the NOAAPort feed of HRRR data does not have radiation, we should
 download this manually from NCEP

Run at 40 AFTER for the previous hour

"""

import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Optional

import click
import httpx
import pygrib
from pyiem.util import archive_fetch, exponential_backoff, logger, utc

LOG = logger()


def need_to_run(valid) -> bool:
    """Check to see if we already have the radiation data we need"""
    ppath = valid.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf01.grib2")
    with archive_fetch(ppath) as fn:
        if fn is None:
            return True
        # Look for our grids please.
        with pygrib.open(fn) as grbs:
            hits = 0
            for grb in grbs:
                if grb.shortName in ["dswrf", "msdwswrf"]:
                    hits += 1
    LOG.info("Found %s dswrf fields in %s", hits, ppath)
    return hits != 4


def fetch(valid):
    """Fetch the radiation data for this timestamp
    22:23684154:d=2023041000:DSWRF:surface:0-15 min ave fcst:
    """
    baseuri = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod"
    if valid < utc() - timedelta(days=1):
        baseuri = "https://noaa-hrrr-bdp-pds.s3.amazonaws.com"
    uri = valid.strftime(
        f"{baseuri}/hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsubhf01.grib2.idx"
    )
    req = exponential_backoff(httpx.get, uri, timeout=30)
    if req is None or req.status_code != 200:
        LOG.warning("failed to get idx %s", uri)
        return

    offsets = []
    neednext = False
    for line in req.content.decode("utf-8").split("\n"):
        tokens = line.split(":")
        if len(tokens) < 3:
            continue
        if neednext:
            offsets[-1].append(int(tokens[1]))
            neednext = False
        if (
            tokens[3]
            in [
                "DSWRF",
            ]
            and tokens[5].find("ave fcst") > -1
        ):
            offsets.append([int(tokens[1])])
            neednext = True

    if len(offsets) != 4:
        LOG.warning("warning, found %s gribs for %s", len(offsets), valid)
    # Force overwrite first
    routes = "a"
    for pr in offsets:
        pqstr = valid.strftime(
            f"data {routes} %Y%m%d%H00 bogus "
            "model/hrrr/%H/hrrr.t%Hz.3kmf01.grib2 grib2"
        )
        routes = "u"
        headers = {"Range": f"bytes={pr[0]}-{pr[1]}"}
        req = exponential_backoff(
            httpx.get, uri[:-4], headers=headers, timeout=30
        )
        if req is None:
            LOG.info("failure for uri: %s", uri)
            continue
        with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
            tmpfd.write(req.content)
        subprocess.call(["pqinsert", "-p", pqstr, tmpfd.name])
        os.unlink(tmpfd.name)


@click.command()
@click.option("--valid", type=click.DateTime(), help="Specify UTC valid time")
def main(valid: Optional[datetime]):
    """Go Main Go"""
    times = []
    if valid is not None:
        times.append(valid.replace(tzinfo=timezone.utc))
    else:
        times.append(utc() - timedelta(hours=1))
        times.append(utc() - timedelta(hours=6))
        times.append(utc() - timedelta(hours=24))
    for ts in times:
        if not need_to_run(ts):
            continue
        LOG.info("running for %s", ts)
        fetch(ts)


if __name__ == "__main__":
    main()
