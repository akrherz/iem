# Generate analysis of precipitation

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
select s.station, s.network,
  x(s.geom) as lon, y(s.geom) as lat, 
  (case when s.pday < 0 then 0 else s.pday end) as rainfall
from summary_%s s, current c
WHERE s.station = c.station and c.valid > (now() - '2 hours'::interval)
and day = 'TODAY' and s.network = c.network
and (s.network ~* 'ASOS' or s.network = 'AWOS') and s.network != 'IQ_ASOS'
""" % (now.year, )

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] + (random.random() * 0.01))
  vals.append( rs[i]['rainfall'] )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_ASOS']) )

if len(lats) < 3:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_showvalues'        : True,
 '_format'            : '%.2f',
 '_MaskZero'          : True,
 '_title'             : "Iowa ASOS/AWOS Rainfall Reports",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[inch]",
 '_valuemask'         : valmask
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 summary/today_prec.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
