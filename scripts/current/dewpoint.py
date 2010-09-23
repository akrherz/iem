# Generate current plot of visibility

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
  station, network, dwpf, drct, sknt, x(geom) as lon, y(geom) as lat
FROM 
  current_log
WHERE
  (network ~* 'ASOS' or network = 'IA_AWOS') and
  valid BETWEEN '2010-04-22 11:50' and '2010-04-22 12:00' and
  dwpf >= -30 and dwpf < 100
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] + (random.random() * 0.01))
  lons.append( rs[i]['lon'] )
  vals.append( uv(rs[i]['sknt'], rs[i]['drct'])[0]  )
  #valmask.append(  (rs[i]['network'] in ['AWOS','IA_AWOS']) )
  valmask.append(  False )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Dew Point",
 '_valid'             : now.strftime("%d %b %Y %-I:%M %p"),
 '_showvalues'        : True,
 '_format'            : '%.1f',
 '_midwest'           : True,
 '_valuemask'         : valmask,
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 iowa_dwpf.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
