"""Download and archive 1000 ft reflectivity from the NCEP HRRR"""
from __future__ import print_function
import sys
import os
import subprocess
import logging
import datetime

import pytz
import requests
import pygrib
from pyiem.util import utc, exponential_backoff

# HRRR model hours available
HOURS = [
    36,
    18,
    18,
    18,
    18,
    18,
    36,
    18,
    18,
    18,
    18,
    18,
    36,
    18,
    18,
    18,
    18,
    18,
    36,
    18,
    18,
    18,
    18,
    18,
]
BASE = "http://www.ftp.ncep.noaa.gov/data/nccf/com/hrrr/prod/"


def upstream_has_data(valid):
    """Does data exist upstream to even attempt a download"""
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    # NCEP should have at least 24 hours of data
    return (utcnow - datetime.timedelta(hours=24)) < valid


def run(valid):
    """ run for this valid time! """
    if not upstream_has_data(valid):
        return
    gribfn = valid.strftime(
        (
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
            "hrrr.t%Hz.refd.grib2"
        )
    )
    if os.path.isfile(gribfn):
        # See how many grib messages we have
        try:
            grbs = pygrib.open(gribfn)
            if grbs.messages == (18 * 4 + (HOURS[valid.hour] - 18) + 1):
                # print("%s is complete!" % (gribfn, ))
                return
            del grbs
        except Exception as exp:
            logging.debug(exp)
    tmpfn = "/tmp/%s.grib2" % (valid.strftime("%Y%m%d%H"),)
    output = open(tmpfn, "wb")
    for hr in range(0, min([39, HOURS[valid.hour]]) + 1):
        shr = "%02i" % (hr,)
        if hr <= 18:
            uri = valid.strftime(
                (
                    BASE
                    + "hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsubhf"
                    + shr
                    + ".grib2.idx"
                )
            )
        else:
            uri = valid.strftime(
                (
                    BASE
                    + "hrrr.%Y%m%d/conus/hrrr.t%Hz.wrfsfcf"
                    + shr
                    + ".grib2.idx"
                )
            )
        req = exponential_backoff(requests.get, uri, timeout=30)
        if req is None or req.status_code != 200:
            print("dl_hrrrref failed to fetch %s" % (uri,))
            print("ABORT")
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

        if hr > 0 and hr < 19 and len(offsets) != 4:
            print(
                ("dl_hrrrref[%s] hr: %s offsets: %s")
                % (valid.strftime("%Y%m%d%H"), hr, offsets)
            )
        for pr in offsets:
            headers = {"Range": "bytes=%s-%s" % (pr[0], pr[1])}
            req = exponential_backoff(requests.get, uri[:-4], headers=headers)
            if req is None:
                print("dl_hrrrref FAIL %s %s" % (uri[:-4], headers))
                continue
            output.write(req.content)

    output.close()
    # insert into LDM Please
    pqstr = (
        "data a %s bogus " "model/hrrr/%02i/hrrr.t%02iz.refd.grib2 grib2"
    ) % (valid.strftime("%Y%m%d%H%M"), valid.hour, valid.hour)
    subprocess.call(
        "/home/ldm/bin/pqinsert -p '%s' %s" % (pqstr, tmpfn),
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    os.unlink(tmpfn)


def main(argv):
    """ Go Main Go """
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    run(valid)


if __name__ == "__main__":
    # do main
    main(sys.argv)
