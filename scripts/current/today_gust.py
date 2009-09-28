# Generate analysis of Peak Wind Gust

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
select s.station, s.network,
  x(s.geom) as lon, y(s.geom) as lat, 
  case when s.max_sknt > s.max_gust then s.max_sknt else s.max_gust END  as wind
from summary s, current c
WHERE s.station = c.station and c.valid > 'TODAY' and s.day = 'TODAY'
and (s.network ~* 'ASOS' or s.network = 'AWOS')
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] + (random.random() * 0.01))
  vals.append( rs[i]['wind'] * 1.16 )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_ASOS']) )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa ASOS/AWOS Peak Wind Speed Reports",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[mph]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025,
 '_valuemask'         : valmask
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/today_gust.png bogus png' tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
