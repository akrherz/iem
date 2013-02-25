"""
Check a raster file and count the number of non-zero values
"""
from osgeo import gdal
import numpy
import sys

ntp = gdal.Open('/home/ldm/data/gis/images/4326/USCOMP/ntp_0.png')
data = ntp.ReadAsArray()
count = numpy.sum( numpy.where(data > 0, 1, 0)  )
sz = data.shape[0] * data.shape[1]

if count > 1000:
    print 'OK - %s/%s|count=%s;100;500;1000' % (count, sz, count)
    sys.exit(0)
elif count > 500:
    print 'WARNING - %s/%s|count=%s;100;500;1000' % (count, sz, count)
    sys.exit(1)
else:
    print 'CRITICAL - %s/%s|count=%s;100;500;1000' % (count, sz, count)
    sys.exit(2)
