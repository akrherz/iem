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

xref = {}
rs = mesosite.query("SELECT id, climate_site, x(geom) as lon, y(geom) as lat from stations WHERE network in ('IA_ASOS', 'AWOS')").dictresult()
for i in range(len(rs)):
  xref[ rs[i]['id'] ] = rs[i]

h2008 = {}
rs = coop.query("select stationid, max(high) from alldata WHERE year = 2008 GROUP by stationid").dictresult()
for i in range(len(rs)):
 h2008[ rs[i]['stationid'] ] = rs[i]['max']

vals = []
lats = []
lons = []
rs = iem.query("SELECT station, max(max_tmpf) from summary WHERE network IN ('IA_ASOS','AWOS') and max_tmpf < 100 GROUP by station").dictresult()
for i in range(len(rs)):
  id = rs[i]['station']
  cid = xref[ id ]['climate_site'].lower()
  high08 = h2008[ cid ]
  high = rs[i]['max']
  vals.append( high - high08 )
  lats.append( xref[id]['lat'] )
  lons.append( xref[id]['lon'] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Max High for 2009 versus all of 2008",
 '_valid'             : now.strftime("%d %b %Y"),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 tmp.ps tmp.png")
