"""Download and archive 1000 ft reflectivity from the NCEP HRRR"""
import sys
import os
import subprocess
import logging
import datetime
import time

import requests
import pygrib
from pyiem.util import utc, exponential_backoff, logger

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
    LOG.debug("using %s as dl service", service)
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
    tmpfn = "/tmp/%s.grib2" % (valid.strftime("%Y%m%d%H"),)
    output = open(tmpfn, "wb")
    for hr in range(0, min([39, HOURS[valid.hour]]) + 1):
        if should_throttle and hr > 30:
            # Add some delays to work around upstream connection throttling
            time.sleep(60)
        shr = "%02i" % (hr,)
        if hr <= 18:
            uri = valid.strftime(
                f"{service}hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsubhf{shr}.grib2.idx"
            )
        else:
            uri = valid.strftime(
                f"{service}hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsfcf{shr}.grib2.idx"
            )
        LOG.debug(uri)
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
            headers = {"Range": "bytes=%s-%s" % (pr[0], pr[1])}
            req = exponential_backoff(requests.get, uri[:-4], headers=headers)
            if req is None:
                LOG.info("dl_hrrrref FAIL %s %s", uri[:-4], headers)
                continue
            output.write(req.content)

    output.close()
    # insert into LDM Please
    pqstr = (
        "data a %s bogus model/hrrr/%02i/hrrr.t%02iz.refd.grib2 grib2"
    ) % (valid.strftime("%Y%m%d%H%M"), valid.hour, valid.hour)
    subprocess.call(
        "pqinsert -p '%s' %s" % (pqstr, tmpfn),
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    os.unlink(tmpfn)


def main(argv):
    """Go Main Go"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    run(valid)


if __name__ == "__main__":
    # do main
    main(sys.argv)
