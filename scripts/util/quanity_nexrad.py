# Look for missing files of composite reflectivity, if found, run the
# cache script

import mx.DateTime
import sys, os

sts = mx.DateTime.DateTime( int(sys.argv[1]), 1, 1)
ets = sts + mx.DateTime.RelativeDateTime(years=1)
now = sts
interval = mx.DateTime.RelativeDateTime(minutes=5)
cnt = 0
while (now < ets):
  if now > mx.DateTime.gmt():
    sys.exit()
  fp = "/mesonet/ARCHIVE/data/%s/%02i/%02i/comprad/n0r_%s.png" % (now.year, now.month, now.day, now.strftime("%Y%m%d_%H%M") ) 
  if (not os.path.isfile(fp)):
    print 'MISS', fp
    cmd = "/mesonet/python/bin/python ../dl/radar_composite.py %s" % (
         now.strftime("%Y %m %d %H %M") )
    os.system( cmd )
    cnt += 1
  else:
    sz = len( open(fp,'r').read() )
    if (sz < 2000):
      print fp, sz
  now += interval

print sts, cnt
