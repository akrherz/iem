# Generate analysis of Peak Wind Gust

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
  case when s.max_sknt > s.max_gust then s.max_sknt else s.max_gust END  as wind
from summary_%s s, current c
WHERE s.station = c.station and c.valid > 'TODAY' and s.day = 'TODAY'
and (s.network ~* 'ASOS' or s.network = 'AWOS') and s.network != 'IQ_ASOS'
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  if rs[i]['wind'] == 0:
    continue
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] + (random.random() * 0.01))
  vals.append( rs[i]['wind'] * 1.16 )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_ASOS']) )

if len(vals) < 5:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa ASOS/AWOS Peak Wind Speed Reports",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[mph]",
 '_valuemask'         : valmask
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
        now.strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
