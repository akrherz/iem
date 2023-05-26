"""Check the availability of NEXRAD Mosiacs.

called from RUN_0Z.sh
"""
import datetime
import os
import sys

from pyiem.util import logger, utc

LOG = logger()


def run(sts, ets):
    """Loop over a start to end time and look for missing N0Q products."""

    now = sts
    interval = datetime.timedelta(minutes=5)
    while now < ets:
        for comp in ["us", "ak", "hi", "pr", "gu"]:
            fn = (
                f"/mesonet/ARCHIVE/data/{now:%Y/%m/%d}/GIS/{comp}comp/"
                f"n0q_{now:%Y%m%d%H%M}.png"
            )
            if not os.path.isfile(fn):
                LOG.warning("[%s]%s is missing", comp, os.path.basename(fn))
            elif comp == "us" and os.stat(fn)[6] < 200000:
                LOG.warning(
                    "check_n0q.py %s too small, size: %s",
                    os.path.basename(fn),
                    os.stat(fn)[6],
                )
        now += interval


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        sts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        utcnow = utc()
        sts = utcnow - datetime.timedelta(hours=24)
        sts = sts.replace(hour=0, minute=0, second=0, microsecond=0)
    ets = sts + datetime.timedelta(hours=24)
    run(sts, ets)


if __name__ == "__main__":
    main(sys.argv)
