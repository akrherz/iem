# Generate current plot of visibility

import sys, os
sys.path.append("../lib/")
import iemplot, random

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
SELECT 
  station, network, vsby, x(geom) as lon, y(geom) as lat
FROM 
  current
WHERE
  network IN ('AWOS', 'IA_ASOS','IL_ASOS','MN_ASOS','WI_ASOS','SD_ASOS',
              'NE_ASOS','MO_ASOS') and
  valid + '15 minutes'::interval > now() and
  vsby >= 0 and vsby < 20
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['vsby'] + (random.random() * 0.001) )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_AWOS']) )

cfg = {
 'wkColorMap': 'gsdtol',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Visibility",
 '_valid'             : now.strftime("%d %b %Y %-I:%M %p"),
 '_showvalues'        : True,
 '_format'            : '%.1f',
 '_valuemask'         : valmask,
 'lbTitleString'      : "[miles]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 iowa_vsby.png bogus png"
iemplot.postprocess(tmpfp, pqstr, "-rotate -90")
