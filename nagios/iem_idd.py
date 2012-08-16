"""
 Nagios check to make sure we have data flowing through LDM 
"""
import sys
import os
import stat
import datetime

now = datetime.datetime.now()
mtime = os.stat("/home/ldm/data/mesonet.gif")[stat.ST_MTIME]
ts = datetime.datetime.fromtimestamp(mtime)
diff = (now - ts).days * 86400. + (now - ts).seconds
if diff < 1800:
    print 'OK - mesonet.gif %s' % (ts,)
    sys.exit(0)
elif diff < 3600:
    print 'WARNING - mesonet.gif %s' % (ts,)
    sys.exit(1)
else:
    print 'CRITICAL - mesonet.gif %s' % (ts,)
    sys.exit(2)