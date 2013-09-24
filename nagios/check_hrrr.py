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
        now = now - datetime.timedelta(hours=1)
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                          +"hrrr.t%Hz.3kmf00.grib2"))
        if not os.path.isfile(fn):
            continue
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400. + (now - ts).seconds
        break

    return diff
    
if __name__ == '__main__':
    diff = check()
    if diff is not None and diff < 7200:
        print 'OK - %s age' % (diff,)
        sys.exit(0)
    elif diff is not None and diff < 10800:
        print 'WARNING - %s age' % (diff)
        sys.exit(1)
    else:
        print 'CRITICAL - %s age' % (diff,)
        sys.exit(2)