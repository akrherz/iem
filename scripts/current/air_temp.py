# Generate current plot of air temperature

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
  station, network, tmpf, x(geom) as lon, y(geom) as lat
FROM 
  current
WHERE
  network IN ('AWOS', 'IA_ASOS','IL_ASOS','MN_ASOS','WI_ASOS','SD_ASOS',
              'NE_ASOS','MO_ASOS') and
  valid + '15 minutes'::interval > now() and
  tmpf > -50
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['tmpf'] )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_AWOS']) )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa 2 Meter Air Temperature",
 '_valid'             : now.strftime("%d %b %Y %-I:%M %p"),
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

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 tmp.ps iowa_tmpf.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 iowa_tmpf.png bogus png' iowa_tmpf.png")
os.remove("iowa_tmpf.png")
os.remove("tmp.ps")
