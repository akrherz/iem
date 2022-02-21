"""Check the availability of NEXRAD Mosiacs."""
import datetime
import os
import sys

from pyiem.util import utc, logger

LOG = logger()


def run(sts, ets):
    """Loop over a start to end time and look for missing N0Q products."""

    now = sts
    interval = datetime.timedelta(minutes=5)
    while now < ets:
        fn = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0q_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fn):
            LOG.warning("%s is missing", os.path.basename(fn))
        else:
            if os.stat(fn)[6] < 200000:
                LOG.warning(
                    "check_n0q.py %s too small, size: %s",
                    fn.split("/")[-1],
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
