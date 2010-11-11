# Generate current plot of air temperature

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
iem = i['iem']
mesosite = i['mesosite']

vals = []
lats = []
lons = []
rs = iem.query("SELECT station, x(geom) as lon, y(geom) as lat, min(min_tmpf) from summary_2010 WHERE network IN ('IA_ASOS','AWOS') and day >= '2010-04-01' and station not in ('DNS','AXA') and day < '2010-05-01' GROUP by station, lon, lat ORDER by min DESC").dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['min'] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  print rs[i]['station'], rs[i]['min']

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2010 April Minimum Temperature",
 '_valid'             : "1-31 Apr 2010",
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, "")
