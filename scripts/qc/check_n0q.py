"""Check the availability of NEXRAD Mosiacs.

called from RUN_0Z.sh
"""
import datetime
import os
import sys

from pyiem.util import archive_fetch, logger, utc

LOG = logger()


def run(sts, ets):
    """Loop over a start to end time and look for missing N0Q products."""

    now = sts
    interval = datetime.timedelta(minutes=5)
    while now < ets:
        for comp in ["us", "ak", "hi", "pr", "gu"]:
            ppath = f"{now:%Y/%m/%d}/GIS/{comp}comp/n0q_{now:%Y%m%d%H%M}.png"
            with archive_fetch(ppath) as fn:
                if fn is None:
                    LOG.warning("[%s]%s is missing", comp, ppath)
                    continue
                if comp == "us" and os.stat(fn)[6] < 200000:
                    LOG.warning(
                        "%s too small, size: %s",
                        ppath,
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
