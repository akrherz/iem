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


sql = """
SELECT 
  station, c.network, tmpf, drct, sknt, x(s.geom) as lon, y(s.geom) as lat
FROM 
  current c, stations s
WHERE
  (c.network ~* 'ASOS' or c.network = 'AWOS') and s.country = 'US' and
  s.id = c.station and s.network = c.network and 
  (valid + '30 minutes'::interval) > now() and
  tmpf >= -50 and tmpf < 140
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

cfg['_midwest'] = True
cfg['_showvalues'] = False
cfg['_title'] = 'Midwest 2 meter Air Temperature'

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s00 midwest_tmpf.png midwest_tmpf_%s.png png" % (
                mx.DateTime.gmt().strftime("%Y%m%d%H"),
                mx.DateTime.gmt().strftime("%H"))
iemplot.postprocess(tmpfp, pqstr)

del(cfg['_midwest'])
cfg['_conus'] = True
cfg['_title'] = 'US 2 meter Air Temperature'

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s00 conus_tmpf.png conus_tmpf_%s.png png" % (
                mx.DateTime.gmt().strftime("%Y%m%d%H"),
                mx.DateTime.gmt().strftime("%H"))
iemplot.postprocess(tmpfp, pqstr)
