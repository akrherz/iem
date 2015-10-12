'''
 Check to make sure we have HRRR model data flowing to the IEM archives
'''
import os
import sys
import datetime


def check():
    ''' Do the chec please '''
    now = datetime.datetime.utcnow()
    diff = None
    for hr in range(8):
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                           "hrrr.t%Hz.3kmf00.grib2"))
        now = now - datetime.timedelta(hours=1)
        if not os.path.isfile(fn):
            continue
        diff = hr
        break

    return diff, now

if __name__ == '__main__':
    diff, now = check()
    stats = "|age=%s;4;5;6" % (diff if diff is not None else -1,)
    if diff is not None and diff < 6:
        print 'OK - %sz found %s' % (now.strftime("%H"), stats)
        sys.exit(0)
    elif diff is not None:
        print 'WARNING - %sz found %s' % (now.strftime("%H"), stats)
        sys.exit(1)
    else:
        print 'CRITICAL - no HRRR found %s' % (stats,)
        sys.exit(2)
