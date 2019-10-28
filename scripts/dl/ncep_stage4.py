"""
 Script to download the NCEP stage4 data and then inject into LDM for
 sweet archival action
"""
from __future__ import print_function
import datetime
import os
import subprocess

import pytz
import requests
from pyiem.util import exponential_backoff


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
                    "http://ftpprd.ncep.noaa.gov/"
                    "data/nccf/com/pcpanl/prod/"
                    "pcpanl.%Y%m%d/"
                    "ST4.%Y%m%d%H"
                )
            ),
            hr,
        )
        response = exponential_backoff(requests.get, url, timeout=60)
        if response is None or response.status_code != 200:
            if offset > 23:
                print("ncep_stage4.py: dl %s failed" % (url,))
            continue
        # Same temp file
        output = open("tmp.grib.gz", "wb")
        output.write(response.content)
        output.close()
        subprocess.call("gunzip -f tmp.grib.gz", shell=True)
        # Inject into LDM
        cmd = (
            "/home/ldm/bin/pqinsert -p 'data a %s blah "
            "stage4/ST4.%s.%02ih.grib grib' tmp.grib"
        ) % (now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H"), hr)
        subprocess.call(cmd, shell=True)
        os.remove("tmp.grib")

        # Do stage2 ml now
        if hr == 1:
            url = "%s.Grb.gz" % (
                now.strftime(
                    (
                        "http://ftpprd.ncep.noaa.gov"
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
                        "http://ftpprd.ncep.noaa.gov/"
                        "data/nccf/com/pcpanl/prod/"
                        "pcpanl.%Y%m%d/"
                        "ST2ml%Y%m%d%H"
                    )
                ),
                hr,
            )
        response = exponential_backoff(requests.get, url, timeout=60)
        if response is None or response.status_code != 200:
            if offset > 23:
                print("ncep_stage4.py: dl %s failed" % (url,))
            continue
        # Same temp file
        output = open("tmp.grib.gz", "wb")
        output.write(response.content)
        output.close()
        subprocess.call("gunzip -f tmp.grib.gz", shell=True)
        # Inject into LDM
        cmd = (
            "/home/ldm/bin/pqinsert -p 'data a %s blah "
            "stage4/ST2ml.%s.%02ih.grib grib' tmp.grib"
        ) % (now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H"), hr)
        subprocess.call(cmd, shell=True)
        os.remove("tmp.grib")


def main():
    """ Do something """
    # We want this hour GMT
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.utc, minute=0, second=0, microsecond=0)
    for offset in [33, 9, 3, 0]:
        now = utc - datetime.timedelta(hours=offset)
        download(now, offset)


if __name__ == "__main__":
    main()
