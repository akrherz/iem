# Generate current plot of air temperature

import sys, os, numpy
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

vals = []
valmask = []
lats = []
lons = []
rs = postgis.query("""SELECT state, 
      max(magnitude) as val, x(geom) as lon, y(geom) as lat
      from lsrs_2009 WHERE type = 'S' and 
      valid > now() - '6 hours'::interval
      GROUP by state, lon, lat""").dictresult()
for i in range(len(rs)):
  vals.append( rs[i]['val'] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  valmask.append( rs[i]['state'] in ['IA',] )
  #valmask.append( False )

# Now, we need to add in zeros, lets say we are looking at a .25 degree box
buffer = 0.25
for lat in numpy.arange(iemplot.IA_SOUTH, iemplot.IA_NORTH, buffer):
  for lon in numpy.arange(iemplot.IA_WEST, iemplot.IA_EAST, buffer):
    found = False
    for j in range(len(lats)):
      if (lats[j] > lat and lats[j] < (lat+buffer) and
         lons[j] > lon and lons[j] < (lon+buffer) ):
        found = True
    if not found:
      lats.append( lat )
      lons.append( lon )
      valmask.append( False )
      vals.append( 0 )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_valuemask'         : valmask,
 '_title'             : "Local Storm Report Snowfall Total Analysis",
 '_valid'             : "Reports past 6 hours: "+ now.strftime("%d %b %Y %I:%M %p"),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_MaskZero'          : True,
 'lbTitleString'      : "[in]",
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
