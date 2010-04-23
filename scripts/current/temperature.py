# Generate current plot of Temperature

import sys, os, math
sys.path.append("../lib/")
import iemplot, random

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
iem = i['iem']

def uv(sped, drct2):
  #print "SPED:", sped, type(sped), "DRCT2:", drct2, type(drct2)
  dirr = drct2 * math.pi / 180.00
  s = math.sin(dirr)
  c = math.cos(dirr)
  u = round(- sped * s, 2)
  v = round(- sped * c, 2)
  return u, v

# Compute normal from the climate database
sql = """
SELECT 
  station, network, tmpf, drct, sknt, x(geom) as lon, y(geom) as lat
FROM 
  current
WHERE
  (network ~* 'ASOS' or network = 'IA_AWOS') and
  (valid + '30 minutes'::interval) > now() and
  tmpf >= -50 and tmpf < 120
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] + (random.random() * 0.01))
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['tmpf']  )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_AWOS']) )
  #valmask.append(  False )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa 2 meter Air Temperature",
 '_valid'             : now.strftime("%d %b %Y %-I:%M %p"),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_valuemask'         : valmask,
 'lbTitleString'      : "[F]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 iowa_tmpf.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
