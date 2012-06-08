# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=1)

import pg
wepp = pg.connect('wepp', 'iemdb', user='nobody')

# Compute normal from the climate database
sql = """
select station, 
  x(geom) as lon, y(geom) as lat, 
  max(day) as maxday
from summary 
WHERE pday >= 0.25
and (network ~* 'ASOS' or network = 'AWOS')
GROUP by station, lon, lat
"""

sql = """
SELECT x(transform(centroid(the_geom),4326)) as lon, 
       y(transform(centroid(the_geom),4326)) as lat, maxday from
 (SELECT hrap_i, max(valid) as maxday from daily_rainfall_2012 
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
  lons.append( rs[i]['lon'] + (random.random() * 0.01))
  vals.append( (now -ts).days )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Days since last 0.5in plus Daily Rainfall",
 '_valid'             : "%s" % ( now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[days]",
#'cnFillMode'          : 'CellFill',
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)
