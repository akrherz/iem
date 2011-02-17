# Generate current plot of air temperature

import sys, os
#sys.path.append("../lib/")
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
rs = iem.query("""SELECT station, x(geom) as lon, y(geom) as lat, 
  max(max_tmpf) as data from summary_2010 WHERE network IN ('IA_ASOS','AWOS') 
  and day >= '2010-12-01' and station not in ('DNSS') 
  and max_tmpf > -30 
  GROUP by station, lon, lat ORDER by data DESC""").dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['data'] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  print rs[i]['station'], rs[i]['data']

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2010 December Maximum Temperature",
 '_valid'             : "1-28 Dec 2010",
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
