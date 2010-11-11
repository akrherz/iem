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
rs = iem.query("SELECT station, x(geom) as lon, y(geom) as lat, min_tmpf from summary_2010 WHERE network IN ('IA_ASOS','AWOS','IA_COOP') and day = '2010-05-09' and min_tmpf < 80 and station not in ('ORC') ORDER by min_tmpf DESC").dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['min_tmpf'] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  print rs[i]['station'], rs[i]['min_tmpf']

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "9 May 2010 Low Temperature",
 '_valid'             : "",
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, "")
