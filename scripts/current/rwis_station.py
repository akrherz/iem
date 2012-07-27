"""
 Iowa RWIS station plot!
"""

import sys
import os
import iemplot
import synop

import mx.DateTime
now = mx.DateTime.now()
import psycopg2.extras
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Compute normal from the climate database
sql = """
SELECT 
  s.id, tmpf, dwpf, sknt, drct,  x(s.geom) as lon, y(s.geom) as lat
FROM 
  current c, stations s 
WHERE
  s.network IN ('IA_RWIS') and c.iemid = s.iemid and 
  valid + '20 minutes'::interval > now() and
  tmpf > -50 and s.id not in ('RLMI4', 'ROCI4', 'RMYI4', 'RAII4')
"""

lats = []
lons = []
vals = []
icursor.execute(sql)
for row in icursor:
    lats.append( row['lat'] )
    lons.append( row['lon'] )
    imdat = synop.ob2synop( row )
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
