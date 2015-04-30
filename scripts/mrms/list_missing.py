"""List out missing MRMS data files for a month"""
import datetime
import os
import sys


def main(argv):
    """Go Main"""

    sts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]), 0, 0)
    ets = datetime.datetime(int(argv[4]), int(argv[5]), int(argv[6]), 0, 0)
    interval = datetime.timedelta(hours=1)
    now = sts
    while now < ets:
        fn = now.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/RadarOnly_QPE_01H/"
                          "RadarOnly_QPE_01H_00.00_%Y%m%d-%H0000.grib2.gz"))
        if not os.path.isfile(fn):
            print("Missing: %s" % (fn.split("/")[-1],))
        now += interval

if __name__ == '__main__':
    main(sys.argv)
