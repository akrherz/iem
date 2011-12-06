# Generate current plot of air temperature

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

vals = []
lats = []
lons = []
icursor.execute("SELECT id, x(geom) as lon, y(geom) as lat, min(min_tmpf) from summary_2011 s JOIN stations t on (t.iemid = s.iemid) WHERE network IN ('IA_ASOS','AWOS') and min_tmpf > 20 and day > '2011-08-01' and id not in ('OLZ','CWI','BNW','AXA') GROUP by id, lon, lat ORDER by min DESC")
for row in icursor:
  vals.append( row[3] )
  lats.append( row[2] )
  lons.append( row[1] )
  print row[3], row[0]

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
