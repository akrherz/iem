"""
 Script to download the NCEP stage4 data and then inject into LDM for
 sweet archival action

run from RUN_STAGE4.sh
"""
import datetime
import os
import subprocess
import tempfile

import requests
from pyiem.util import exponential_backoff, logger, utc

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
        url = (
            "https://nomads.ncep.noaa.gov/pub/data/nccf/com/pcpanl/"
            f"prod/pcpanl.{now:%Y%m%d}/st4_conus.{now:%Y%m%d%H}."
            f"{hr:02.0f}h.grb2"
        )
        LOG.info("fetching %s", url)
        response = exponential_backoff(requests.get, url, timeout=60)
        if response is None or response.status_code != 200:
            if offset > 23:
                LOG.info("dl %s failed", url)
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
    for offset in [33, 9, 3, 0]:
        with tempfile.TemporaryDirectory() as tempdir:
            os.chdir(tempdir)
            download(utcnow - datetime.timedelta(hours=offset), offset)


if __name__ == "__main__":
    main()
