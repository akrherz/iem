"""Attempt to fill missing MRMS files

Sadly, the NCEP LDM MRMS feed sometimes misses important files! We need to
look at our archive and attempt to fill those holes.

Run from RUN_12Z.sh
"""
import datetime
import sys
import os
import requests
from pyiem.util import exponential_backoff
import tempfile
import subprocess
import logging

logging.basicConfig()
logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

PRODS = {'GaugeCorr_QPE_01H': datetime.timedelta(minutes=60),
         'PrecipFlag': datetime.timedelta(minutes=2),
         'PrecipRate': datetime.timedelta(minutes=2),
         'RadarOnly_QPE_01H': datetime.timedelta(minutes=60),
         'RadarOnly_QPE_24H': datetime.timedelta(minutes=60),
         'SeamlessHSR': datetime.timedelta(minutes=2)}


def fetch(prod, now):
    """We have work to do!"""
    uri = now.strftime(("http://mrms.ncep.noaa.gov/data/2D/" +
                        prod + "/MRMS_" + prod +
                        "_00.00_%Y%m%d-%H%M%S.grib2.gz"))

    logger.debug("Fetching %s" % (uri,))
    res = exponential_backoff(requests.get, uri, timeout=60)
    if res is None or res.status_code != 200:
        logger.error("fill_mrms_holes failed to dl: %s" % (uri,))
        return
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, res.content)
    os.close(tmpfd)

    pattern = now.strftime(("/data/realtime/outgoing/grib2/"
                            "MRMS_" + prod + "_00.00_" +
                            "%Y%m%d-%H%M%S.grib2.gz"))
    cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % (pattern, tmpfn)
    subprocess.call(cmd, shell=True)
    os.remove(tmpfn)


def do(prod, sts, ets):
    """Process this stuff now!"""
    now = sts
    while now < ets:
        fn = now.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/" +
                           prod + "/" + prod + "_00.00_%Y%m%d-%H%M%S.grib2.gz"
                           ))
        if not os.path.isfile(fn):
            logger.info("%s is missing for time: %s" % (prod, now))
            fetch(prod, now)
        now += PRODS.get(prod)


def main(argv):
    """Do Something"""
    ets = datetime.datetime.utcnow().replace(minute=0, second=0,
                                             microsecond=0)
    sts = ets - datetime.timedelta(hours=24)
    [do(prod, sts, ets) for prod in PRODS]

if __name__ == '__main__':
    main(sys.argv)
