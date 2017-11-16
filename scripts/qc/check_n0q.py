"""
Check the availability of NEXRAD Composites
"""
from __future__ import print_function
import datetime
import os
import sys
import pytz


def run(sts, ets):
    ''' Loop over a start to end time and look for missing N0Q products '''

    now = sts
    interval = datetime.timedelta(minutes=5)
    while now < ets:
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/"
                           "uscomp/n0q_%Y%m%d%H%M.png"))
        if not os.path.isfile(fn):
            print('check_n0q.py %s is missing' % (fn.split("/")[-1],))
        else:
            if os.stat(fn)[6] < 200000:
                print(('check_n0q.py %s too small, size: %s'
                       ) % (fn.split("/")[-1], os.stat(fn)[6]))
        now += interval


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        sts = datetime.datetime(int(argv[1]), int(argv[2]),
                                int(argv[3]))
        sts = sts.replace(tzinfo=pytz.utc)
    else:
        utc = datetime.datetime.utcnow()
        utc = utc.replace(tzinfo=pytz.utc)
        sts = utc - datetime.timedelta(hours=24)
        sts = sts.replace(hour=0, minute=0, second=0, microsecond=0)
    ets = sts + datetime.timedelta(hours=24)
    run(sts, ets)


if __name__ == '__main__':
    main(sys.argv)
