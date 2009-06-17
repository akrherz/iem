# Generate a plot of NWS COOP precip reports

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
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  val = rs[i]['pday']
  if val > 0:
    vals.append("%.2f" % (rs[i]['pday'],) )
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
iemplot.simple_valplot(lons, lats, vals, cfg)

os.system("convert -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 iowa_coop_precip.png bogus png' tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
