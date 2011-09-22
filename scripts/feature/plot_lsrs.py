# Generate current plot of air temperature

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

vals = []
valmask = []
lats = []
lons = []
rs = postgis.query("""SELECT state, 
      max(magnitude) as val, x(geom) as lon, y(geom) as lat
      from lsrs_2011 WHERE type = 'G' and 
      valid > '2011-06-26 12:00' and state = 'IA' and magnitude > 0 
      GROUP by state, lon, lat""").dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['val'] * 1.15 )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  valmask.append( rs[i]['state'] in ['IA',] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_valmask'           : valmask,
 '_title'             : "Wind Gust Local Storm Reports [mph]",
 '_valid'             : "Reports from noon 26 Jun 2011 to 6 AM 27 Jun 2011",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
#iemplot.postprocess(tmpfp, '')
iemplot.makefeature(tmpfp)

#os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
#os.system("xv tmp.png")
