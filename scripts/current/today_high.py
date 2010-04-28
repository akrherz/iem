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
  max_tmpf as high
from summary_%s
WHERE day = 'TODAY' and max_tmpf > -40 
and network in ('IA_ASOS', 'AWOS')
""" % (now.year, )

lats = []
lons = []
vals = []
valmask = []
labels = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['high'] )
  labels.append( rs[i]['station'] )
  valmask.append( True )

if len(rs) < 5:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa ASOS/AWOS Today High Temperature",
 '_valid'             : "%s" % (now.strftime("%d %b %Y %-I:%M %p"), ),
 '_labels'            : labels
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot ac %s summary/iowa_asos_high.png iowa_asos_high.png png" % (
        now.strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
