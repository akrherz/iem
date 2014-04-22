# Set GIS Satellite data! :)

# 15 after scan produced at 45 after
# 45 after scan produced at 15 after

import datetime
import sys

#ftp://gp16.ssd.nesdis.noaa.gov/pub/GIS/GOESwest/GoesWest1V3501745.tif

now = datetime.datetime.utcnow()

cycle = sys.argv[1]

if cycle == "15":
    now = now.replace(minute=15)
else:
    now -= datetime.timedelta(hours=1)
    now = now.replace(minute=45)

print now.strftime("%Y%m%d%H%M")
