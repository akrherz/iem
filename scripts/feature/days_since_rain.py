# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']
wepp = i['wepp']

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
 (SELECT hrap_i, max(valid) as maxday from daily_rainfall_2009 
  WHERE rainfall / 25.4 > 0.24 GROUP by hrap_i) as dr, hrap_polygons h
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
 '_title'             : "Iowa Days since last 0.25in plus Rainfall",
 '_valid'             : "%s" % ( now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[days]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
#os.remove("tmp.png")
#os.remove("tmp.ps")
