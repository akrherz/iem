# Generate a plot of GDD for the ASOS/AWOS network

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """SELECT station, x(geom) as lon, y(geom) as lat,
   sum(gdd50(max_tmpf, min_tmpf)) as gdd, 
   sum(sdd86(max_tmpf, min_tmpf)) as sdd 
   from summary_%s WHERE network in ('IA_ASOS','AWOS') and
   extract(month from day) = extract(month from now())
   GROUP by station, lon, lat""" % (now.year,)

lats = []
lons = []
gdd50 = []
sdd86 = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  gdd50.append( rs[i]['gdd'] )
  sdd86.append( rs[i]['sdd'] )
  valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_valueMask'         : valmask,
 '_format'            : '%.0f',
 '_title'             : "Iowa %s GDD Accumulation" % (
                        now.strftime("%B %Y"), ),
 'lbTitleString'      : "[base 50]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, gdd50, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 +repage -density 120 tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/gdd_mon.png bogus png' tmp.png")
if os.environ['USER'] == 'akrherz':
  os.system("xv tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
