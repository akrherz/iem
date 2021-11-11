""" Create symlink for calendar day precip totals

The processing scripts create 24hour RASTERs based on UTC date, for some apps
like IDEP, we'd like predictable calendar day rasters

Run from RUN_MIDNIGHT.sh

"""
import sys
import os
import datetime

try:
    from zoneinfo import ZoneInfo  # type: ignore
except ImportError:
    from backports.zoneinfo import ZoneInfo

from pyiem.util import logger

LOG = logger()


def workflow(basedate, utcdt):
    """Create the sym link"""
    basefn = utcdt.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/mrms/p24h_%Y%m%d%H00"
    )
    for suffix in ["png", "wld"]:
        target = f"{basefn}.{suffix}"
        if not os.path.isfile(target):
            LOG.info("ERROR: %s not found", target)
            return
        linkfn = basedate.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/mrms_calday_%Y%m%d"
        )
        link = f"{linkfn}.{suffix}"
        if os.path.islink(link):
            LOG.info("Skipping link creation, already exists %s", link)
            continue
        LOG.debug("%s -> %s", target, link)
        os.symlink(target, link)


def main(argv):
    """Do Something"""
    # Start off at noon
    basedt = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]), 12)
    basedt = basedt.replace(tzinfo=ZoneInfo("America/Chicago"))
    # Now set to midnight tomorrow
    basedt += datetime.timedelta(hours=24)
    localdt = basedt.replace(hour=0)
    # Now get our UTC equiv
    utcdt = localdt.astimezone(ZoneInfo("Etc/UTC"))
    workflow(basedt, utcdt)


if __name__ == "__main__":
    # Go Main Go
    main(sys.argv)
