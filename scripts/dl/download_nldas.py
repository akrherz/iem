"""Fetch the NLDAS forcing-a files for archiving
Run at 00 UTC and get the files from 4 days ago!
"""
import datetime
import subprocess
import tempfile
import os

import requests
from pyiem.util import logger, utc, exponential_backoff

LOG = logger()


def do(ts):
    """ Run for a given date! """
    for hr in range(24):
        now = ts.replace(hour=hr, minute=0, second=0)

        uri = now.strftime(
            "https://ftpprd.ncep.noaa.gov/data/nccf/com/nldas/"
            "prod/nldas.%Y%m%d/nldas.t12z.force-a.grb2f"
        ) + "%02i" % (hr,)

        try:
            req = exponential_backoff(requests.get, uri, timeout=60)
            if req is None or req.status_code != 200:
                raise Exception(
                    "status code is %s"
                    % (0 if req is None else req.status_code,)
                )
        except Exception:
            LOG.info("download failed for: %s", uri)
            continue
        tmpfd = tempfile.NamedTemporaryFile(delete=False)
        tmpfd.write(req.content)
        tmpfd.close()

        cmd = (
            "pqinsert -p 'data a %s bogus "
            "model/nldas/nldas.t12z.force-a.grb2f%02i grib2' %s"
        ) % (now.strftime("%Y%m%d%H%M"), hr, tmpfd.name)
        LOG.debug(cmd)
        subprocess.call(cmd, shell=True)

        os.remove(tmpfd.name)


def main():
    """Go Main Go"""
    ts = utc() - datetime.timedelta(days=5)
    do(ts)


if __name__ == "__main__":
    main()
