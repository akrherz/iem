# Generate current plot of Temperature

import sys, os, math
sys.path.append("../lib/")
import iemplot, random

import mx.DateTime
now = mx.DateTime.now()

import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)


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
  (network ~* 'ASOS' or network = 'AWOS') and network != 'IQ_ASOS' and
  (valid + '30 minutes'::interval) > now() and
  tmpf >= -50 and tmpf < 120
"""

lats = []
lons = []
vals = []
valmask = []
icursor.execute( sql )
for row in icursor:
  lats.append( row['lat'] )
  lons.append( row['lon'] )
  vals.append( row['tmpf']  )
  valmask.append(  (row['network'] in ['AWOS','IA_ASOS']) )
  #valmask.append(  False )
print valmask

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
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s00 iowa_tmpf.png iowa_tmpf_%s.png png" % (
                mx.DateTime.gmt().strftime("%Y%m%d%H"),
                mx.DateTime.gmt().strftime("%H"))
iemplot.postprocess(tmpfp, pqstr)
