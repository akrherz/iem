"""Download the 5km FFG product.

Run from RUN_40_AFTER.sh
"""

import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Optional

import click
import httpx
from pyiem.util import archive_fetch, exponential_backoff, logger, utc

LOG = logger()


def do(ts):
    """Run for a given date!"""
    ppath = ts.strftime("%Y/%m/%d/model/ffg/5kmffg_%Y%d%m%H.grib2")
    with archive_fetch(ppath) as fn:
        if fn is not None:
            LOG.info("Already have %s", ppath)
            return
    remotefn = ts.strftime("5kmffg_%Y%m%d%H.grb2")
    url = f"https://ftp.wpc.ncep.noaa.gov/workoff/ffg/{remotefn}"
    LOG.info("fetching %s", url)
    req = exponential_backoff(httpx.get, url, timeout=20)
    if req is None or req.status_code != 200:
        LOG.warning("Download of %s failed", url)
        return
    tmpfd, tmpfn = tempfile.mkstemp()
    os.write(tmpfd, req.content)
    os.close(tmpfd)
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        f"data a {ts:%Y%m%d%H%M} bogus model/ffg/{remotefn[:-5]}.grib2 grib2",
        tmpfn,
    ]
    LOG.info(cmd)
    subprocess.call(cmd)

    os.remove(tmpfn)


@click.command()
@click.option("--valid", type=click.DateTime(), help="Specify UTC valid time")
def main(valid: Optional[datetime]):
    """Go Main Go"""
    if valid is None:
        # Run for the last hour, when we are modulus 6
        ts = utc() - timedelta(hours=1)
        ts = ts.replace(minute=0)
        if ts.hour % 6 > 0:
            LOG.info("Aborting as timestamp %s is not modulus 6", ts)
            return
    else:
        ts = valid.replace(tzinfo=timezone.utc)
    # NOTE website no longer has 3 days worth of data, but two
    for offset in [0, 24, 36]:
        do(ts - timedelta(hours=offset))


if __name__ == "__main__":
    main()
