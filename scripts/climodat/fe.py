import mx.DateTime
import os

sts = mx.DateTime.DateTime(2009,6,1)
ets = mx.DateTime.DateTime(2009,10,21)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
while now < ets:
  print now
  os.system("/mesonet/python/bin/python daily_estimator.py %s" % (now.strftime("%Y %m %d"),))
  os.system("/mesonet/python/bin/python compute_ia0000.py %s" % (now.strftime("%Y %m %d"),))
  now += interval
