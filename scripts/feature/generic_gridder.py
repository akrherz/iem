# Generate current plot of air temperature

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

vals = []
valmask = []
lats = []
lons = []
rs = iem.query("""SELECT  
      max(max_tmpf) as val, x(geom) as lon, y(geom) as lat
      from summary_2010 WHERE network ~* 'ASOS'
      and max_tmpf > 0 and max_tmpf < 90 GROUP by lon, lat
      """).dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['val'] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  #valmask.append( rs[i]['state'] in ['IA',] )
  valmask.append( False )

cfg = {
 'wkColorMap': 'WhViBlGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,

 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 4.0,
 'cnMinLevelValF'       : 10.0,
 'cnMaxLevelValF'       : 60.0,

 '_valuemask'         : valmask,
 '_midwest'           : True,
 '_title'             : "2010 Maximum Temperature",
 '_valid'             : "1 Jan thru "+ now.strftime("%d %b %Y"),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 lsr_snowfall.png bogus png' tmp.png")
if os.environ['USER'] == 'akrherz':
  os.system("xv tmp.png")
  sys.exit()
os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 320x210 -density 120 +repage tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 lsr_snowfall_thumb.png bogus png' tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
