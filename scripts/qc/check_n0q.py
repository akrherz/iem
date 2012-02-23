"""
Check the availability of NEXRAD Composites
"""
import mx.DateTime
import os

sts = mx.DateTime.DateTime(2012,2,19,0,0)
ets = mx.DateTime.DateTime(2012,2,23,21,0)
interval = mx.DateTime.RelativeDateTime(minutes=5)
now = sts

while now < ets:
  fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0q_%Y%m%d%H%M.png")
  if not os.path.isfile(fp):
    print 'MISSING', now
  else:
    if os.stat(fp)[6] < 600000:
      print 'Too Small', now, os.stat(fp)[6]
  now += interval
