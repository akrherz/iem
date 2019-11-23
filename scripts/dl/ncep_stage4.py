"""
 Script to download the NCEP stage4 data and then inject into LDM for
 sweet archival action
"""
import datetime
import os
import subprocess

import requests
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()


def download(now, offset):
    """
    Download a given timestamp from NCEP and inject into LDM
    Example:  ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/hourly/prod/
              nam_pcpn_anal.20090916/ST4.2009091618.01h.gz
    """
    hours = [1]
    if now.hour % 6 == 0 and offset > 24:
        hours.append(6)
    if now.hour == 12:
        hours.append(24)
    for hr in hours:
        url = "%s.%02ih.gz" % (
            now.strftime(
                (
                    "https://ftpprd.ncep.noaa.gov/data/nccf/com/pcpanl/prod/"
                    "pcpanl.%Y%m%d/ST4.%Y%m%d%H"
                )
            ),
            hr,
        )
        LOG.debug("fetching %s", url)
        response = exponential_backoff(requests.get, url, timeout=60)
        if response is None or response.status_code != 200:
            if offset > 23:
                LOG.info("dl %s failed", url)
            continue
        # Same temp file
        with open("tmp.grib.gz", "wb") as fh:
            fh.write(response.content)
        subprocess.call("gunzip -f tmp.grib.gz", shell=True)
        # Inject into LDM
        cmd = (
            "pqinsert -p 'data a %s blah "
            "stage4/ST4.%s.%02ih.grib grib' tmp.grib"
        ) % (now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H"), hr)
        subprocess.call(cmd, shell=True)
        os.remove("tmp.grib")

        # Do stage2 ml now
        if hr == 1:
            url = "%s.Grb.gz" % (
                now.strftime(
                    (
                        "https://ftpprd.ncep.noaa.gov"
                        "/data/nccf/com/pcpanl/prod/"
                        "pcpanl.%Y%m%d/"
                        "ST2ml%Y%m%d%H"
                    )
                ),
            )
        else:
            url = "%s.%02ih.gz" % (
                now.strftime(
                    (
                        "https://ftpprd.ncep.noaa.gov/"
                        "data/nccf/com/pcpanl/prod/"
                        "pcpanl.%Y%m%d/"
                        "ST2ml%Y%m%d%H"
                    )
                ),
                hr,
            )
        LOG.debug("fetching %s", url)
        response = exponential_backoff(requests.get, url, timeout=60)
        if response is None or response.status_code != 200:
            if offset > 23:
                LOG.info("dl %s failed", url)
            continue
        # Same temp file
        with open("tmp.grib.gz", "wb") as fh:
            fh.write(response.content)
        subprocess.call("gunzip -f tmp.grib.gz", shell=True)
        # Inject into LDM
        cmd = (
            "pqinsert -p 'data a %s blah "
            "stage4/ST2ml.%s.%02ih.grib grib' tmp.grib"
        ) % (now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H"), hr)
        subprocess.call(cmd, shell=True)
        os.remove("tmp.grib")


def main():
    """ Do something """
    # We want this hour UTC
    utcnow = utc()
    utcnow = utcnow.replace(minute=0, second=0, microsecond=0)
    for offset in [33, 9, 3, 0]:
        download(utcnow - datetime.timedelta(hours=offset), offset)


if __name__ == "__main__":
    main()
