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
rs = iem.query("SELECT station, x(geom) as lon, y(geom) as lat, max(max_tmpf) from summary WHERE network IN ('IA_ASOS','AWOS') and day > '2009-12-01' and station != 'CKP' GROUP by station, lon, lat ORDER by max DESC").dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['max'] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  print rs[i]['station'], rs[i]['max']

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Max Temperature since 2 Dec 2009",
 '_valid'             : now.strftime("%d %b %Y"),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage %s.ps %s.png" % (fp,fp))
if os.environ['USER'] == 'akrherz':
  os.system("xv %s.png" % (fp,))

