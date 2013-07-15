"""
Generates the nice 4inch soil temperature plot by county
"""
from pyiem.plot import MapPlot
import numpy as np
import datetime
import os
import sys
from scipy.interpolate import NearestNDInterpolator
import network
import matplotlib.cm as cm
import psycopg2.extras
nt = network.Table("ISUAG")

ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
icursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)

day_ago = int(sys.argv[1])
ts = datetime.datetime.now() - datetime.timedelta(days=day_ago)

# Query out the data
soil_obs = []
lats = []
lons = []
icursor.execute("""SELECT station, c30 from daily WHERE 
     valid = '%s' and c30 > 0 and station not in ('A135849','A131909')""" % (
     ts.strftime("%Y-%m-%d"), ) )
for row in icursor:
    stid = row['station']
    soil_obs.append( row['c30'] )
    lats.append( nt.sts[stid]['lat'] )
    lons.append( nt.sts[stid]['lon'] )

if len(lats) < 5:
    sys.exit()

def sampler(xaxis, yaxis, vals, x, y):
    i = 0
    while (xaxis[i] < x):
        i += 1
    j = 0
    while (yaxis[j] < y):
        j += 1
    return vals[i,j]

# Grid it
numxout = 40
numyout = 40
xmin    = min(lons) - 2.
ymin    = min(lats) - 2.
xmax    = max(lons) + 2.
ymax    = max(lats) + 2.
xc      = (xmax-xmin)/(numxout-1)
yc      = (ymax-ymin)/(numyout-1)

xo = xmin + xc * np.arange(0,numxout)
yo = ymin + yc * np.arange(0,numyout)

#analysis = griddata((lons, lats), soil_obs, (xo, yo) )
#rbfi = Rbf(lons, lats, soil_obs, function='cubic')
#analysis = rbfi(xo, yo)
nn = NearestNDInterpolator((lons, lats), np.array(soil_obs))
analysis = nn(xo, yo)

# Query out centroids of counties...
pcursor.execute("""SELECT x(centroid(the_geom)) as lon, 
  y(centroid(the_geom)) as lat 
 from uscounties WHERE state_name = 'Iowa'""")
clons = []
clats = []
for row in pcursor:
    clats.append( row['lat'] )
    clons.append( row['lon'] )

cobs = nn(clons, clats)
#cobs = griddata((lons, lats), soil_obs, (clons, clats))

m = MapPlot(sector='iowa',
    title="Iowa 4in Soil Temperatures %s" % (ts.strftime("%b %d %Y"), ),
    subtitle='Based on gridded analysis of ISUAG network observations'
)
m.contourf(xo, yo, analysis, np.arange(10,101,5), cmap=cm.get_cmap('jet'),
           units=r'$^\circ$F')
for lo, la, ob in zip(clons, clats, cobs):
#for lo, la, ob in zip(lons, lats, soil_obs):
    xi, yi = m.map(lo, la)
    txt = m.ax.text(xi, yi, "%.0f" % (ob,))
m.drawcounties()
m.postprocess(filename='highs.ps')

os.system("convert -trim  highs.ps obs.png")
routes = "a"
if day_ago < 4:
    routes = "ac" 
os.system("/home/ldm/bin/pqinsert -p 'plot %s %s0000 soilt_day%s.png isuag_county_4inch_soil.png png' obs.png" % (
 routes, ts.strftime("%Y%m%d"), day_ago) )
os.unlink('highs.ps')
os.unlink('obs.png')
