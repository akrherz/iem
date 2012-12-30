"""
 Make sure we have current RIDGE imagery
"""
import os
import sys
import stat
import datetime
SAMPLES = ['DMX', 'AMA', 'LWX', 'FFC', 'BMX']

def check():
    now = datetime.datetime.now()
    count = 0
    for nexrad in SAMPLES:
        fn = "/home/ldm/data/gis/images/4326/ridge/%s/N0Q_0.png" % (nexrad,)
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400. + (now - ts).seconds
        if diff > 600:
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