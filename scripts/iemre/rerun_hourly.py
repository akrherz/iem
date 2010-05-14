import mx.DateTime
import stage4_hourlyre

sts = mx.DateTime.DateTime(2010,5,1)
ets = mx.DateTime.DateTime(2010,5,13)
interval = mx.DateTime.RelativeDateTime(hours=1)
now = sts
while now < ets:
  print now
  stage4_hourlyre.merge( now )
  now += interval
