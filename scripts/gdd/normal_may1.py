# Generate a plot of normal GDD Accumulation since 1 May of this year

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()
if now.month < 5 or now.month > 10:
  sys.exit(0)

import network
nt = network.Table('IACLIMATE')
import iemdb
COOP = iemdb.connect('coop', bypass=True)
import psycopg2.extras
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Compute normal from the climate database
sql = """SELECT station, sum(gdd50) as gdd, sum(sdd86) as sdd 
   from climate WHERE gdd50 IS NOT NULL and sdd86 IS NOT NULL and 
   valid >= '2000-05-01' and valid <=
  ('2000-'||to_char(CURRENT_TIMESTAMP, 'mm-dd'))::date 
  and substr(station,0,3) = 'IA' GROUP by station"""

lats = []
lons = []
gdd50 = []
sdd86 = []
ccursor.execute( sql )
for row in ccursor:
  id = row['station']
  lats.append( nt.sts[id]['lat'] )
  lons.append( nt.sts[id]['lon'] )
  gdd50.append( row['gdd'] )
  sdd86.append( row['sdd'] )


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'       : "1 May - %s Average GDD Accumulation" % (
                        now.strftime("%d %b"), ),
 'lbTitleString'      : "[base 50]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)

pqstr = "plot c 000000000000 summary/gdd_norm_may1.png bogus png"
iemplot.postprocess(tmpfp, pqstr)

#---------- Plot the points

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_format': '%.0f',
 '_title'       : "1 May - %s Average GDD Accumulation" % (
                        now.strftime("%d %b"), ),
}


tmpfp = iemplot.simple_valplot(lons, lats, gdd50, cfg)

pqstr = "plot c 000000000000 summary/gdd_norm_may1_pt.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
