# Number of days since the last 0.25 inch rainfall

import sys, os, random
import iemplot

import mx.DateTime
now = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=1)

import pg
wepp = pg.connect('wepp', 'iemdb', user='nobody')

sql = """
SELECT x(transform(centroid(the_geom),4326)) as lon, 
       y(transform(centroid(the_geom),4326)) as lat, maxday from
 (SELECT hrap_i, max(valid) as maxday from daily_rainfall_2013 
  WHERE rainfall / 25.4 > 0.50 GROUP by hrap_i) as dr, hrap_polygons h
 WHERE h.hrap_i = dr.hrap_i
"""

lats = []
lons = []
vals = []
#rs = iem.query(sql).dictresult()
rs = wepp.query(sql).dictresult()
for i in range(len(rs)):
  ts = mx.DateTime.strptime(rs[i]['maxday'], '%Y-%m-%d')
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( (now -ts).days )

import numpy as np
from pyiem.plot import MapPlot
import matplotlib.cm as cm
m = MapPlot(sector='iowa', title='Days since last 0.5+ inch calendar day rainfall', subtitle='based on NOAA Stage IV Estimates')
m.contourf(lons, lats, vals, np.arange(0,61,5), cmap=cm.get_cmap('jet'),
       units='days')
m.drawcounties()
m.postprocess(filename='test.ps')
iemplot.makefeature('test')
