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
rs = iem.query("SELECT station, x(geom) as lon, y(geom) as lat, min(min_tmpf) from summary_2011 WHERE network IN ('IA_ASOS','AWOS') and min_tmpf > 20 and day > '2011-08-01' and station not in ('ORC','TNU') GROUP by station, lon, lat ORDER by min DESC").dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['min'] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  print rs[i]['station'], rs[i]['min']

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2011 Minimum Temperature after 1 August",
 '_valid'             : now.strftime("%d %b %Y"),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)
