# Output the 12z morning low temperature

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

sql = """
select station, 
  x(geom) as lon, y(geom) as lat, 
  min(tmpf) as low12z
from current_log
WHERE tmpf > -40 and valid > '%s 00:00:00+00' and valid < '%s 12:00:00+00' 
and network in ('IA_ASOS', 'AWOS') GROUP by station, lon, lat
""" % (now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))

lats = []
lons = []
vals = []
valmask = []
labels = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['low12z'] )
  labels.append( rs[i]['station'] )
  valmask.append( True )

if len(rs) < 5:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa ASOS/AWOS 12Z Morning Low Temperature",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[F]",
 '_labels'            : labels
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot ac %s summary/iowa_asos_12z_low.png iowa_asos_12z_low.png png" % (
        now.strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
