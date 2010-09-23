# Generate current plot of air temperature

import sys, os
sys.path.append("../lib/")
import iemplot, synop

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
SELECT 
  station, tmpf, dwpf, sknt, drct, x(geom) as lon, y(geom) as lat
FROM 
  current
WHERE
  network IN ('KCCI') and
  valid + '5 minutes'::interval > now() and
  tmpf > -50
"""

lats = []
lons = []
vals = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  imdat = synop.ob2synop( rs[i] )
  vals.append( imdat )
  #vals.append("11206227031102021040300004963056046601517084081470")


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "KCCI-TV SchoolNet Mesoplot",
 '_valid'             : now.strftime("%d %b %Y %-I:%M %p"),
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 '_stationplot' : True,
 '_removeskyc'  : True,
 '_spatialDataLimiter' : True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 iowa_tmpf.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
