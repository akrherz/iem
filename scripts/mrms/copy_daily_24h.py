"""Copies the appropriate MRMS 24 HR raster for a calendar date.

Run from RUN_MIDNIGHT.sh
"""

import datetime
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

from pyiem.util import logger

LOG = logger()


def workflow(dt):
    """Copy things around."""
    basefn = dt.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/mrms/p24h_%Y%m%d%H00"
    )
    yest = dt - datetime.timedelta(days=1)
    for suffix in ["png", "wld"]:
        target = f"{basefn}.{suffix}"
        if not os.path.isfile(target):
            LOG.warning("ERROR: %s not found", target)
            return
        cmd = [
            "pqinsert",
            "-i",
            "-p",
            f"gis a {yest:%Y%m%d%H%M} GIS/mrms_calday_{yest:%Y%m%d}.{suffix} "
            f"GIS/mrms_calday_{yest:%Y%m%d}.{suffix} {suffix}",
            target,
        ]
        subprocess.call(cmd)
        LOG.info("%s -> %s", target, " ".join(cmd))


def main(argv):
    """Do Something"""
    # Compute midnight Central as UTC
    dt = datetime.datetime(
        int(argv[1]),
        int(argv[2]),
        int(argv[3]),
        0,
        tzinfo=ZoneInfo("America/Chicago"),
    ).astimezone(ZoneInfo("UTC"))
    LOG.info("Computed midnight UTC of %s", dt)
    workflow(dt)


if __name__ == "__main__":
    # Go Main Go
    main(sys.argv)
