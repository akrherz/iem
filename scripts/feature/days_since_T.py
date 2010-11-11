# Number of days since the last 0.25 inch rainfall

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
select station, 
  x(geom) as lon, y(geom) as lat, 
  max(day) as maxday
from summary_2010
WHERE min_tmpf < 60
and (network ~* 'ASOS' or network = 'AWOS') 
and network in ('IA_ASOS','AWOS') and
station NOT IN ('ADU', 'AIO') and network != 'IQ_ASOS' and day < '2010-08-24'
GROUP by station, lon, lat ORDER by maxday DESC
"""

lats = []
lons = []
vals = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  print rs[i]
  ts = mx.DateTime.strptime(rs[i]['maxday'], '%Y-%m-%d')
  if rs[i]['lat'] is not None and rs[i]['lon'] is not None and ts.year == 2010:
    lats.append( rs[i]['lat'] + (0.0001 * i))
    lons.append( rs[i]['lon'] )
    vals.append( (now -ts).days - 1)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Days since sub 60 degree temperature",
 '_valid'             : "%s" % ( now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[days]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.postprocess(fp, "")
