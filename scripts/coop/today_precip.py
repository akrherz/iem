# Plot the COOP Precipitation Reports, don't use lame-o x100

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
  pday 
from summary_%s
WHERE day = 'TODAY' and pday >= 0 and pday < 20
and network = 'IA_COOP'
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
  vals.append( rs[i]['pday'] )
  labels.append( rs[i]['station'] )
  valmask.append( True )


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_showvalues'        : True,
 '_format'            : '%.2f',
 '_title'             : "Iowa COOP 24 Hour Precipitation",
 '_valid'             : "ending %s 7 AM" % (now.strftime("%d %b %Y"), ),
# '_labels'            : labels
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot ac %s iowa_coop_precip.png iowa_coop_precip.png png" % (
        now.strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
