# Generate a plot of NWS COOP snow reports

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
SELECT 
  station, network, snow, x(geom) as lon, y(geom) as lat
FROM 
  summary
WHERE
  network IN ('IA_COOP') and
  day = 'TODAY' and snow >= 0
"""

lats = []
lons = []
vals = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  val = rs[i]['snow']
  if val > 0:
    vals.append("%.1f" % (val,) )
  else:
    vals.append("0")

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "NWS COOP 24HR Snowfall [inch]",
 '_valid'             : "%s 7 AM" % (now.strftime("%d %b %Y"),) ,
 '_format'            : '%s',
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 iowa_coop_snow.png bogus png"
iemplot.postprocess( tmpfp, pqstr )
