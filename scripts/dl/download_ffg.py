"""Download the 5km FFG product.

Run from RUN_40_AFTER.sh
"""
import datetime
import subprocess
import tempfile
import os

from pyiem.util import logger, utc, exponential_backoff
import requests

LOG = logger()


def do(ts):
    """Run for a given date!"""
    localfn = ts.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/ffg/5kmffg_%Y%d%m%H.grib2"
    )
    if os.path.isfile(localfn):
        return
    remotefn = ts.strftime("5kmffg_%Y%m%d%H.grb2")
    url = f"https://ftp.wpc.ncep.noaa.gov/workoff/ffg/{remotefn}"
    LOG.debug("fetching %s", url)
    req = exponential_backoff(requests.get, url, timeout=20)
    if req is None or req.status_code != 200:
        LOG.info("Download of %s failed", url)
        return
    tmpfd, tmpfn = tempfile.mkstemp()
    os.write(tmpfd, req.content)
    os.close(tmpfd)
    cmd = (
        "pqinsert -i -p 'data a %s bogus " "model/ffg/%s.grib2 grib2' %s"
    ) % (ts.strftime("%Y%m%d%H%M"), remotefn[:-5], tmpfn)
    LOG.debug(cmd)
    subprocess.call(cmd, shell=True)

    os.remove(tmpfn)


def main():
    """Go Main Go"""
    # Run for the last hour, when we are modulus 6
    ts = utc() - datetime.timedelta(hours=1)
    ts = ts.replace(minute=0)
    if ts.hour % 6 > 0:
        return
    # NOTE website no longer has 3 days worth of data, but two
    for offset in [0, 24, 36]:
        do(ts - datetime.timedelta(hours=offset))


if __name__ == "__main__":
    main()
