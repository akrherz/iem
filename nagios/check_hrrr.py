'''
 Check to make sure we have HRRR model data flowing to the IEM archives
'''
import os
import sys
import stat
import datetime

def check():
    ''' Do the chec please '''
    now = datetime.datetime.utcnow()
    diff = None
    for hr in range(4):
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                          +"hrrr.t%Hz.3kmf00.grib2"))
        now = now - datetime.timedelta(hours=1)
        if not os.path.isfile(fn):
            continue
        diff = hr
        break

    return diff
    
if __name__ == '__main__':
    diff = check()
    if diff is not None and diff < 3:
        print 'OK - %s hr age' % (diff,)
        sys.exit(0)
    elif diff is not None:
        print 'WARNING - %s hr age' % (diff)
        sys.exit(1)
    else:
        print 'CRITICAL - no HRRR found'
        sys.exit(2)