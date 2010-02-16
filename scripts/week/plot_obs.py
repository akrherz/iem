# Generate analysis of precipitation

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
select station, 
  x(geom) as lon, y(geom) as lat, 
  sum(pday) as rainfall
from summary 
WHERE day > ('TODAY'::date - '7 days'::interval) 
and network in ('AWOS', 'IA_ASOS')
and pday > 0 and pday < 30
GROUP by station, lon, lat
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] + (random.random() * 0.01))
  vals.append( rs[i]['rainfall'] )
  valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_valmask'           : valmask,
 '_format'            : '%.2f',
 '_showvalues'        : True,
 '_title'             : "Iowa Past 7 Days Rainfall",
 '_valid'             : "%s - %s inclusive" % ((now - mx.DateTime.RelativeDateTime(days=6)).strftime("%d %b %Y"), now.strftime("%d %b %Y") ),
 'lbTitleString'      : "[inch]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 summary/7day/ia_precip.png bogus png"
iemplot.postprocess(tmpfp, pqstr, "-rotate -90")
