"""
import osgeo.gdal as gdal
import osgeo.gdal_array
from osgeo.gdalconst import *
import numpy as np
import mx.DateTime, os, shutil
import iemdb
import math
from pyiem import reference

def lalo2pt(lon, lat):
  x = int(( -126.0 - lon ) / - 0.01 )
  y = int(( 50.0 - lat ) / 0.01 )
  return x, y

sts = mx.DateTime.DateTime(2014, 4,7,11,0)
ets = mx.DateTime.DateTime(2014,4,8,2,5)
interval = mx.DateTime.RelativeDateTime(minutes=5)

x1,y1 = lalo2pt(reference.IA_WEST, reference.IA_SOUTH)
x2,y2 = lalo2pt(reference.IA_EAST, reference.IA_NORTH)

sz = (y1-y2) * (x2-x1)

now = sts
while (now < ets):
    fp = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/"
    "n0r_%Y%m%d%H%M.png"))
    n0r = gdal.Open(fp, 0)
    n0rd = n0r.ReadAsArray()
    data = n0rd[y2:y1,x1:x2]
    dbz = (data - 7.0) * 5.0
    print "%s,%.2f" % (now.strftime("%Y%m%d%H%M"),
                       np.sum( np.where(dbz>=10,1,0) ) / float(sz) * 100.0)
    now += interval


"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pytz

x = []
y = []
for line in open('area.txt'):
    tokens = line.split(",")
    ts = datetime.datetime.strptime(tokens[0], '%Y%m%d%H%M')
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    x.append(ts)
    y.append(float(tokens[1]))

(fig, ax) = plt.subplots(1, 1)

ax.plot(x, y)
ax.set_ylabel("Percent Coverage over Iowa [%]")
ax.set_title("7 April 2014 - Iowa Areal Coverage of 10+ dBZ Reflectivity")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-I:%M\n%p',
                             tz=pytz.timezone("America/Chicago")))
ax.grid(True)
ax.text(0.2, 0.15, "Morning Storm\nShowers",
        transform=ax.transAxes, ha='center')
ax.text(0.75, 0.15, "Afternoon Instability\nShowers",
        transform=ax.transAxes, ha='center')

fig.savefig('test.png')
