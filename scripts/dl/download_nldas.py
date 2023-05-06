"""Fetch the NLDAS forcing-a files for archiving
Run at 00 UTC and get the files from 4 days ago!
"""
import datetime
import os
import subprocess
import tempfile

import requests
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()


def do(ts):
    """Run for a given date!"""
    for hr in range(24):
        now = ts.replace(hour=hr, minute=0, second=0)

        uri = (
            "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nldas/"
            f"prod/nldas.{now:%Y%m%d}/nldas.t12z.force-a.grb2f{hr:02.0f}"
        )
        try:
            req = exponential_backoff(requests.get, uri, timeout=60)
            if req is None or req.status_code != 200:
                raise RuntimeError(
                    f"status code is {0 if req is None else req.status_code}"
                )
        except Exception as exp:
            LOG.warning("download failed for: %s, %s", uri, exp)
            continue
        tmpfd = tempfile.NamedTemporaryFile(delete=False)
        tmpfd.write(req.content)
        tmpfd.close()

        cmd = [
            "pqinsert",
            "-p",
            (
                f"data a {now:%Y%m%d%H%M} bogus "
                f"model/nldas/nldas.t12z.force-a.grb2f{hr:02.0f} grib2"
            ),
            tmpfd.name,
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)

        os.remove(tmpfd.name)


def main():
    """Go Main Go"""
    ts = utc() - datetime.timedelta(days=5)
    do(ts)


if __name__ == "__main__":
    main()
