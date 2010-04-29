# Iowa RWIS station plot!

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
  station, tmpf, dwpf, sknt, drct,  x(geom) as lon, y(geom) as lat
FROM 
  current
WHERE
  network IN ('IA_RWIS') and
  valid + '20 minutes'::interval > now() and
  tmpf > -50 and station not in ('RLMI4', 'ROCI4', 'RMYI4', 'RAII4')
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
 '_title'             : "Iowa DOT RWIS Mesoplot",
 '_valid'             : now.strftime("%d %b %Y %-I:%M %p"),
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 '_stationplot' : True,
 '_removeskyc'  : True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 iowa_rwis.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
