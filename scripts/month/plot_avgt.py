# Plot the average temperature for the month

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Compute normal from the climate database
sql = """
SELECT station, s.network, x(s.geom) as lon, y(s.geom) as lat, 
avg( (max_tmpf + min_tmpf)/2.0 ) as avgt , count(*) as cnt 
from summary_%s c, stations s
WHERE (c.network ~* 'ASOS' or c.network = 'AWOS') and 
c.network != 'IQ_ASOS' and c.network = s.network and s.id = c.station and
extract(month from day) = extract(month from now()) 
and max_tmpf > -30 and min_tmpf < 90 GROUP by station, s.network, lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
icursor.execute(sql)
for row in icursor:
  if row['cnt'] != now.day:
    continue
  lats.append( row['lat'] )
  lons.append( row['lon'] )
  vals.append( row['avgt'] )
  valmask.append(  (row['network'] in ['AWOS','IA_ASOS']) )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa %s Average Temperature" % (now.strftime("%Y %B"),),
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
