"""
 Script to download the NCEP stage4 data and then inject into LDM for
 sweet archival action

run from RUN_STAGE4.sh
"""

import datetime
import os
import subprocess
import tempfile

import httpx
from pyiem.util import logger, utc

LOG = logger()


def download(now, offset):
    """
    Download a given timestamp from NCEP and inject into LDM
    Example:  pub/data/nccf/com/hourly/prod/
              nam_pcpn_anal.20090916/ST4.2009091618.01h.gz
    """
    hours = [1]
    if now.hour % 6 == 0 and offset > 24:
        hours.append(6)
    if now.hour == 12:
        hours.append(24)
    for hr in hours:
        upath = (
            "/data/nccf/com/pcpanl/"
            f"prod/pcpanl.{now:%Y%m%d}/st4_conus.{now:%Y%m%d%H}."
            f"{hr:02.0f}h.grb2"
        )
        response = None
        for center in ["ftpprd.ncep.noaa.gov", "nomads.ncep.noaa.gov/pub"]:
            try:
                url = f"https://{center}{upath}"
                LOG.info("fetching %s", url)
                response = httpx.get(url, timeout=60)
                response.raise_for_status()
            except httpx.HTTPError as exp:
                LOG.info("dl %s failed: %s", url, exp)
                continue
            if offset > 23:
                LOG.warning("dl %s failed", url)
            if offset > 0:
                break
        if response is None or response.status_code != 200:
            LOG.info("Full fail for %s", url)
            continue
        # Same temp file
        with open("tmp.grib", "wb") as fh:
            fh.write(response.content)
        # Inject into LDM
        cmd = [
            "pqinsert",
            "-p",
            (
                f"data a {now:%Y%m%d%H%M} blah stage4/ST4.{now:%Y%m%d%H}."
                f"{hr:02.0f}h.grib grib"
            ),
            "tmp.grib",
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)


def main():
    """Do something"""
    # We want this hour UTC
    utcnow = utc()
    utcnow = utcnow.replace(minute=0, second=0, microsecond=0)
    # Website review seems to show updates ~8 days later :/
    for offset in [0, 240, 8 * 24, 9, 3]:
        with tempfile.TemporaryDirectory() as tempdir:
            os.chdir(tempdir)
            download(utcnow - datetime.timedelta(hours=offset), offset)


if __name__ == "__main__":
    main()
