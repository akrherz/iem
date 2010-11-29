# Generate a plot of NWS COOP precip reports

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
SELECT 
  station, network, pday, x(geom) as lon, y(geom) as lat
FROM 
  current
WHERE
  network IN ('IA_COOP') and
  valid > 'TODAY' and pday >= 0
"""

lats = []
lons = []
vals = []
icursor.execute( sql )
for row in icursor:
  lats.append( row[4] )
  lons.append( row[3] )
  val = row[2]
  if val > 0:
    vals.append("%.2f" % (val,) )
  else:
    vals.append("0")

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "NWS COOP 24HR Precipitation",
 '_valid'             : "%s 7 AM" % (now.strftime("%d %b %Y"),) ,
 '_format'            : '%s',
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 iowa_coop_precip.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
