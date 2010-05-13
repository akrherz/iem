import mx.DateTime
import grid_climodat

sts = mx.DateTime.DateTime(2010,1,1)
ets = mx.DateTime.DateTime(2010,5,13)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
while now < ets:
  print now
  grid_climodat.main( now )
  now += interval
