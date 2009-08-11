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
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 +repage -density 120 tmp.ps iowa_vsby.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 iowa_vsby.png bogus png' iowa_vsby.png")
if os.environ['USER'] == 'akrherz':
  os.system("xv iowa_vsby.png")
os.remove("iowa_vsby.png")
os.remove("tmp.ps")
