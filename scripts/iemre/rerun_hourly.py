import mx.DateTime
import stage4_hourlyre
import sys

yr = int(sys.argv[1])
mo = int(sys.argv[2])

sts = mx.DateTime.DateTime(yr,mo,1)
ets = sts + mx.DateTime.RelativeDateTime(months=1)
interval = mx.DateTime.RelativeDateTime(hours=1)
now = sts
while now < ets:
  print now
  stage4_hourlyre.merge( now )
  now += interval
