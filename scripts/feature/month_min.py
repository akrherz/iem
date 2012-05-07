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
icursor.execute("""SELECT id, x(geom) as lon, y(geom) as lat, 
  min(min_tmpf) from summary_2012 s JOIN stations t on (t.iemid = s.iemid)
  WHERE network IN ('IA_ASOS','AWOS') 
  and min_tmpf < 60 and day >= '2012-04-08' and id not in ('CIN', 'TNU')
  GROUP by id, lon, lat ORDER by min DESC""")
for row in icursor:
  vals.append( row[3] )
  lats.append( row[2] )
  lons.append( row[1] )
  print row

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2012 April Minimum Temperature",
 '_valid'             : "April 8th thru 11th",
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp, '','')
import iemplot
iemplot.makefeature(fp)

