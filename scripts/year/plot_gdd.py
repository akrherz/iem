# Generate a plot of GDD for the ASOS/AWOS network

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

gfunc = "gdd50"
gbase = 50
if len(sys.argv) == 2 and sys.argv[1] == "gdd52":
  gfunc = "gdd52"
  gbase = 52

# Compute normal from the climate database
sql = """SELECT station, x(geom) as lon, y(geom) as lat,
   sum(%s(max_tmpf, min_tmpf)) as gdd
   from summary_%s WHERE network in ('IA_ASOS','AWOS')
   and station not in ('ADU','AXA','DNS','CWI','TVK')
   GROUP by station, lon, lat""" % (gfunc, now.year)

lats = []
lons = []
gdd50 = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  if rs[i]['lat'] is None:
    print rs[i]
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  gdd50.append( rs[i]['gdd'] )
  valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_valueMask'         : valmask,
 '_format'            : '%.0f',
 '_title'             : "Iowa %s GDD (base=%s) Accumulation" % (
                        now.strftime("%Y"), gbase),
 '_valid'          : "1 Jan - %s" % (
                        now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[base 50]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)

pqstr = "plot c 000000000000 summary/gdd_jan1.png bogus png"
if gbase == 52:
  pqstr = "plot c 000000000000 summary/gdd52_jan1.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
