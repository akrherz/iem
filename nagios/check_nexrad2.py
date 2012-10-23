"""
 Make sure our nexrad files are current!
"""
import os
import sys
import stat
import datetime
SAMPLES = ['KDMX', 'KAMA', 'KLWX', 'KFFC', 'KBMX']

def check():
    now = datetime.datetime.now()
    count = 0
    for nexrad in SAMPLES:
        fn = "/mnt/mtarchive/nexrd2/raw/%s/dir.list" % (nexrad,)
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400. + (now - ts).seconds
        if diff > 300:
            count += 1
    return count
    
if __name__ == '__main__':
    badcount = check()
    if badcount < 2:
        print 'OK - %s/%s outage' % (badcount, len(SAMPLES))
        sys.exit(0)
    elif badcount < 3:
        print 'WARNING - %s/%s outage' % (badcount, len(SAMPLES))
        sys.exit(1)
    else:
        print 'CRITICAL - %s/%s outage' % (badcount, len(SAMPLES))
        sys.exit(2)