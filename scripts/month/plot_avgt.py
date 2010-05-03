# Plot the average temperature for the month

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
SELECT station, network, x(geom) as lon, y(geom) as lat, 
avg( (max_tmpf + min_tmpf)/2.0 ) as avgt 
from summary_%s
WHERE (network ~* 'ASOS' or network = 'AWOS') and network != 'IQ_ASOS' and
extract(month from day) = extract(month from now()) 
and max_tmpf > -30 and min_tmpf < 90 GROUP by station, network, lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  vals.append( rs[i]['avgt'] )
  valmask.append(  (rs[i]['network'] in ['AWOS','IA_ASOS']) )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa 2009 %s Average Temperature" % (now.strftime("%B"),),
 '_valid'             : "Average of the High + Low ending: %s" % (now.strftime("%d %B"),),
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_valuemask'         : valmask,
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 summary/mon_mean_T.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
