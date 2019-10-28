""" Create symlink for calendar day precip totals

The processing scripts create 24hour RASTERs based on UTC date, for some apps
like IDEP, we'd like predictable calendar day rasters

Run from RUN_MIDNIGHT.sh

"""
from __future__ import print_function
import sys
import os
import datetime
import pytz


def workflow(basedate, utcdt):
    """ Create the sym link """
    basefn = utcdt.strftime(
        ("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/" "mrms/p24h_%Y%m%d%H00")
    )
    for suffix in ["png", "wld"]:
        target = "%s.%s" % (basefn, suffix)
        if not os.path.isfile(target):
            print("MRMS create_daily_symlink ERROR: %s not found" % (target,))
            return
        linkfn = basedate.strftime(
            ("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/" "mrms_calday_%Y%m%d")
        )
        link = "%s.%s" % (linkfn, suffix)
        if os.path.islink(link):
            print("Skipping link creation, already exists %s" % (link,))
            continue
        os.symlink(target, link)


def main(argv):
    """Do Something"""
    # Start off at noon
    basedt = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]), 12, 0)
    localdt = basedt.replace(tzinfo=pytz.utc)
    localdt = localdt.astimezone(pytz.timezone("America/Chicago"))
    # Now set to midnight tomorrow
    localdt += datetime.timedelta(hours=24)
    localdt = localdt.replace(hour=0)
    # Now get our UTC equiv
    utcdt = localdt.astimezone(pytz.utc)
    workflow(basedt, utcdt)


if __name__ == "__main__":
    # Go Main Go
    main(sys.argv)
