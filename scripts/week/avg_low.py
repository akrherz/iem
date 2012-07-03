# Generate mean low temperature for the week

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
select id, 
  x(s.geom) as lon, y(s.geom) as lat, 
  avg(min_tmpf) as min_tmpf
from summary_%s c, stations s
WHERE max_tmpf > -50 
and day >= ('TODAY'::date - '7 days'::interval)
and day < 'TODAY' 
and s.network ~* 'ASOS' and s.country = 'US'
and s.iemid = c.iemid 
GROUP by id, lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
icursor.execute( sql )
for row in icursor:
  lats.append( row[2] )
  lons.append( row[1] )
  vals.append( row[3] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Past 7 Days Average Low",
 '_valid'             : "%s - %s" % ((now - mx.DateTime.RelativeDateTime(days=7)).strftime("%d %b %Y"), now.strftime("%d %b %Y") ),
 'lbTitleString'      : "[F]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 summary/7day/iaavg_min_tmpf.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
