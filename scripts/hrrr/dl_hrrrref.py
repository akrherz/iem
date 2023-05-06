"""Download and archive 1000 ft reflectivity from the NCEP HRRR"""
import datetime
import logging
import os
import subprocess
import sys
import time

import pygrib
import requests
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()
# HRRR model hours available
HOURS = [18] * 24
for _hr in range(0, 24, 6):
    HOURS[_hr] = 48


def get_service(valid):
    """Does data exist upstream to even attempt a download"""
    # NCEP should have at least 24 hours of data
    if (utc() - datetime.timedelta(hours=24)) < valid:
        return "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/"
    return "https://noaa-hrrr-bdp-pds.s3.amazonaws.com/"


def run(valid):
    """run for this valid time!"""
    service = get_service(valid)
    should_throttle = service.find("noaa.gov") > -1
    LOG.info("using %s as dl service", service)
    gribfn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.refd.grib2"
    )
    if os.path.isfile(gribfn):
        # See how many grib messages we have
        try:
            grbs = pygrib.open(gribfn)
            if grbs.messages == (18 * 4 + (HOURS[valid.hour] - 18) + 1):
                return
            del grbs
        except Exception as exp:
            logging.debug(exp)
    tmpfn = f"/tmp/{valid:%Y%m%d%H}.grib2"
    with open(tmpfn, "wb") as output:
        for hr in range(0, HOURS[valid.hour] + 1):
            if should_throttle and hr > 30:
                # Add some delays to work around upstream connection throttling
                time.sleep(15)
            shr = f"{hr:02.0f}"
            if hr <= 18:
                uri = valid.strftime(
                    f"{service}hrrr.%Y%m%d/conus/"
                    f"hrrr.t%Hz.wrfsubhf{shr}.grib2.idx"
                )
            else:
                uri = valid.strftime(
                    f"{service}hrrr.%Y%m%d/conus/"
                    f"hrrr.t%Hz.wrfsfcf{shr}.grib2.idx"
                )
            LOG.info(uri)
            req = exponential_backoff(requests.get, uri, timeout=30)
            if req is None or req.status_code != 200:
                LOG.info("failed to fetch %s", uri)
                if hr > 18:
                    continue
                LOG.info("ABORT")
                return
            data = req.text

            offsets = []
            neednext = False
            for line in data.split("\n"):
                if line.strip() == "":
                    continue
                tokens = line.split(":")
                if neednext:
                    offsets[-1].append(int(tokens[1]))
                    neednext = False
                if tokens[3] == "REFD" and tokens[4] == "1000 m above ground":
                    offsets.append([int(tokens[1])])
                    neednext = True

            if 0 < hr < 19 and len(offsets) != 4:
                LOG.info(
                    "[%s] hr: %s offsets: %s",
                    valid.strftime("%Y%m%d%H"),
                    hr,
                    offsets,
                )
            for pr in offsets:
                headers = {"Range": f"bytes={pr[0]}-{pr[1]}"}
                req = exponential_backoff(
                    requests.get,
                    uri[:-4],
                    headers=headers,
                    timeout=30,
                )
                if req is None:
                    LOG.info("FAIL %s %s", uri[:-4], headers)
                    continue
                output.write(req.content)

    # insert into LDM Please
    pqstr = (
        f"data a {valid:%Y%m%d%H%M} bogus model/hrrr/{valid.hour:02.0f}/"
        f"hrrr.t{valid.hour:02.0f}z.refd.grib2 grib2"
    )
    with subprocess.Popen(
        ["pqinsert", "-p", pqstr, tmpfn],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ) as proc:
        proc.communicate()
    os.unlink(tmpfn)


def main(argv):
    """Go Main Go"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    run(valid)


if __name__ == "__main__":
    # do main
    main(sys.argv)
