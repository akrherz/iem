#!/mesonet/python/bin/python

import mx.DateTime
import os, time

sts = mx.DateTime.DateTime(2008,3,12)
ets = mx.DateTime.DateTime(2009,3,12)
interval = mx.DateTime.RelativeDateTime(days=1)

now = sts
while (now < ets):
  print now
  for q in ['W','S','T']:
    cmd = "./polygonMosaic.py %s %s" % (now.strftime("%Y %m %d"), q)
    os.system( cmd )
  time.sleep(3)
  now += interval
