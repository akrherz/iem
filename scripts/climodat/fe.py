import mx.DateTime
import os

sts = mx.DateTime.DateTime(2011,9,22)
ets = mx.DateTime.DateTime(1949,12,31)
interval = mx.DateTime.RelativeDateTime(days=-1)
now = sts
while now > ets:
  print now
  #for st in ['nd','sd','ne','ks','mo','il','wi','mn','mi','oh','in','ky']:
  #os.system("/mesonet/python/bin/python daily_estimator.py %s %s" % (st, now.strftime("%Y %m %d"),))
  os.system("/mesonet/python/bin/python compute_0000-2.py %s" % (now.strftime("%Y %m %d"),))
  now += interval
