# Plot the year high temperature!

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
SELECT 
  station, x(geom) as lon, y(geom) as lat, max(max_tmpf) as high, network
FROM 
  summary
WHERE
  network IN ('AWOS', 'IA_ASOS','IL_ASOS','MN_ASOS','WI_ASOS','SD_ASOS',
              'NE_ASOS','MO_ASOS') and
  station not in ('IKV','CIN') and day >= '2009-01-01' and day < '2009-05-01' and
  max_tmpf < 130 and max_tmpf > 0 GROUP by station, lon, lat, network
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['high'] )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_ASOS']) )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa 2009 Maximum Temperature",
 '_valid'             : "Jan/Apr 2009",
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_valuemask'         : valmask,
 'lbTitleString'      : "[F]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 +repage -density 120 tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 iowa_vsby.png bogus png' tmp.png")
if os.environ['USER'] == 'akrherz':
  os.system("xv tmp.png")
#os.remove("iowa_vsby.png")
#os.remove("tmp.ps")
