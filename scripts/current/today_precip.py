"""
 Generate analysis of precipitation
"""

import sys
import os
import random
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
select s.id, s.network,
  x(s.geom) as lon, y(s.geom) as lat, 
  (case when c.pday < 0 then 0 else c.pday end) as rainfall
 from summary_%s c, current c2, stations s
 WHERE s.iemid = c2.iemid and c2.iemid = c.iemid and 
 c2.valid > (now() - '2 hours'::interval)
 and c.day = 'TODAY'
 and s.country = 'US' and (s.network ~* 'ASOS' or s.network = 'AWOS')
 and s.state in ('IA','MN','WI','IL','MO','NE','KS','SD','ND')
""" % (now.year, )

lats = []
lons = []
vals = []
iavals = []
valmask = []
icursor.execute(sql)
for row in icursor:
  lats.append( row[3] )
  lons.append( row[2] )
  vals.append( row[4] )
  iowa = row[1] in ['AWOS','IA_ASOS']
  valmask.append( iowa )
  if iowa:
      iavals.append( row[4] )

if len(lats) < 3:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_showvalues'        : True,
 '_format'            : '%.2f',
 '_MaskZero'          : True,
 '_title'             : "Iowa ASOS/AWOS Rainfall Reports",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[inch]",
 '_valuemask'         : valmask
}
# Generates tmp.ps
if max(iavals) < 0.04:
    cfg.pop('lbTitleString')
    tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
else:
    tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot c 000000000000 summary/today_prec.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
