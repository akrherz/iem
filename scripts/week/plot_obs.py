"""
 Generate analysis of precipitation
"""

import sys, os, random
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
select s.id, 
  x(s.geom) as lon, y(s.geom) as lat, 
  sum(pday) as rainfall
 from summary_%s c, stations s
 WHERE day > ('TODAY'::date - '7 days'::interval) 
 and s.network in ('AWOS', 'IA_ASOS')
 and pday >= 0 and pday < 30 and 
 s.iemid = c.iemid
 GROUP by s.id, lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
icursor.execute(sql)
for row in icursor:
    lats.append( row[2] )
    lons.append( row[1] + (random.random() * 0.01))
    vals.append( row[3] )
    valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_valmask'           : valmask,
 '_format'            : '%.2f',
 '_showvalues'        : True,
 '_title'             : "Iowa Past 7 Days Rainfall",
 '_valid'             : "%s - %s inclusive" % ((now - mx.DateTime.RelativeDateTime(days=6)).strftime("%d %b %Y"), now.strftime("%d %b %Y") ),
 'lbTitleString'      : "[inch]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 summary/7day/ia_precip.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
