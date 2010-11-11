# Generate current plot of air temperature

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']
iem = i['iem']

vals = []
valmask = []
lats = []
lons = []
#rs = postgis.query("""SELECT state, 
#      max(magnitude) as val, x(geom) as lon, y(geom) as lat
#      from lsrs_2009 WHERE type = 'S' and 
#      valid > now() - '18 hours'::interval
#      GROUP by state, lon, lat""").dictresult()
rs = iem.query("""SELECT snow as val, x(geom) as lon, y(geom) as lat
     from summary_2010 where network ~* 'COOP' and day = 'TODAY' and
     snow >= 0""").dictresult()
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
 'cnLevelSpacingF'      : .5,
 'cnMinLevelValF'       : .5,
 'cnMaxLevelValF'       : 8.0,

 '_valuemask'         : valmask,
 '_midwest'           : True,
 '_title'             : "24 Hour Snowfall Reports",
 '_valid'             : "Valid: 7 AM - "+ now.strftime("%d %b %Y"),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[in]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage %s.ps %s.png" % (fp,fp))
if os.environ['USER'] == 'akrherz':
  os.system("xv %s.png" % (fp,))
  sys.exit()
os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 320x210 -density 120 +repage tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 lsr_snowfall_thumb.png bogus png' tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
