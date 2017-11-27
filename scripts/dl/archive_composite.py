"""Regenerate composites to fulfill various reasons"""
from __future__ import print_function
import datetime
import sys
from radar_composite import save


def main(argv):
    """Go Main Go"""
    sts = datetime.datetime(int(argv[1]), int(argv[2]),
                            int(argv[3]), int(argv[4]), int(argv[5]))
    ets = datetime.datetime(int(argv[6]), int(argv[7]),
                            int(argv[8]), int(argv[9]), int(argv[10]))
    interval = datetime.timedelta(minutes=5)
    now = sts
    while now < ets:
        print(now)
        text = now.strftime("%Y%m%d%H%M")
        save('conus', 'uscomp.png', 'usrad', text, routes='a')
        save('iem', 'mwcomp.png', 'comprad', text, routes='a')
        for i in ['lot', 'ict', 'sd', 'hun']:
            save(i, '%scomp.png' % (i, ), '%srad' % (i,), text, routes='a')
        now += interval


if __name__ == '__main__':
    main(sys.argv)
