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
   from summary_%s WHERE network in ('IA_ASOS','AWOS')
   GROUP by station, lon, lat""" % (now.year,)

lats = []
lons = []
gdd50 = []
sdd86 = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  if rs[i]['lat'] is None:
    print rs[i]
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
                        now.strftime("%Y"), ),
 'lbTitleString'      : "[base 50]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)

pqstr = "plot c 000000000000 summary/gdd_jan1.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
