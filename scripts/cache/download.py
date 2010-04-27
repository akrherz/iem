#!/mesonet/python/bin/python
# Set GIS Satellite data! :)

# 15 after scan produced at 45 after
# 45 after scan produced at 15 after

import mx.DateTime, sys

#ftp://gp16.ssd.nesdis.noaa.gov/pub/GIS/GOESwest/GoesWest1V3501745.tif

now = mx.DateTime.gmt()

cycle = int(sys.argv[1])

if (cycle == 15):
  now += mx.DateTime.RelativeDateTime(minute=15)
else:
  now += mx.DateTime.RelativeDateTime(minute=45,hours=-1)

print now.strftime("%j%H%M")
