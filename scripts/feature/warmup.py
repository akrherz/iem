# Warmup for the day

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']
wepp = i['wepp']

# Compute normal from the climate database
sql = """
select station, network,
  x(geom) as lon, y(geom) as lat, 
  max_tmpf - min_tmpf as warmup
from summary 
WHERE day = 'TODAY' and max_tmpf > 0 and min_tmpf < 92
and network in ('IA_ASOS', 'AWOS')
"""

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['warmup'] )
  valmask.append( rs[i]['network'] in ['AWOS','IA_ASOS'] )


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_format'            : '%.0f',
 '_showvalues'        : True,
 '_valueMask'         : valmask,
 '_title'             : "Sunday Warmup (High - Low)",
 '_valid'             : "%s" % ( now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[F]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
#os.remove("tmp.png")
#os.remove("tmp.ps")
