"""
 Nagios check to make sure we have data flowing through LDM
"""
import sys
import os
import stat
import datetime

FN = "/home/ldm/data/gis/images/4326/USCOMP/n0q_0.png"
now = datetime.datetime.now()
mtime = os.stat(FN)[stat.ST_MTIME]
ts = datetime.datetime.fromtimestamp(mtime)
diff = (now - ts).days * 86400. + (now - ts).seconds
if diff < 600:
    print 'OK - n0q_0.png %s' % (ts,)
    sys.exit(0)
elif diff < 700:
    print 'WARNING - n0q_0.png %s' % (ts,)
    sys.exit(1)
else:
    print 'CRITICAL - n0q_0.png %s' % (ts,)
    sys.exit(2)
