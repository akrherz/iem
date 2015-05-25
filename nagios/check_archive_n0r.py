"""
Make sure we have archived N0R so that things do not freak out!
"""
import datetime
import sys
import os

now = datetime.datetime.utcnow()
now = now - datetime.timedelta(minutes=now.minute % 5)
base = now

miss = []
for i in range(12):
    fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/"
                       "n0r_%Y%m%d%H%M.png"))
    if not os.path.isfile(fn):
        miss.append(now.strftime("%Y%m%d_%H%M"))
    now -= datetime.timedelta(minutes=5)


if len(miss) == 0:
    print 'OK'
    sys.exit(0)
if len(miss) > 0:
    print 'CRITICAL - %s archive miss N0R %s' % (base.strftime("%d_%H%M"),
                                                 ', '.join(miss),)
    sys.exit(2)
