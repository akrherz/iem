#!/mesonet/python/bin/python

import osgeo.gdal as gdal
import osgeo.gdal_array
from osgeo.gdalconst import *
import numpy, mx.DateTime, os, shutil

def run(x, y):
  sts = mx.DateTime.DateTime(2013,1,16,0)
  ets = mx.DateTime.DateTime(2013,1,17,10)
  interval = mx.DateTime.RelativeDateTime(minutes=5)

  now = sts
  while (now < ets):
    fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png")
    if (not os.path.isfile(fp)):
      print "MISSING:", fp
      now += interval
      continue
    n0r = gdal.Open(fp, 0)
    n0rd = n0r.ReadAsArray()
    val = numpy.average( n0rd[y-2:y+2,x-2:x+2] )
    print "%s,%.1f,%.1f" %(now.strftime("%Y-%m-%d %H:%M"), val, val * 5.0)
    now += interval

lat = 41.6596
lon = -93.522
x = int(( -126.0 - lon ) / - 0.01 )
y = int(( 50.0 - lat ) / 0.01 )

run(x, y)
