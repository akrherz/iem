"""
 Generate analysis of Peak Wind Gust
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
  case when c.max_sknt > c.max_gust then c.max_sknt else c.max_gust END  as wind
  from summary_%s c, current c2, stations s
  WHERE s.iemid = c.iemid and c2.valid > '2012-10-29 12:00' and c.day = 'TODAY'
  and c2.iemid = s.iemid
  and (s.network ~* 'ASOS' or s.network = 'AWOS') and s.country = 'US'
  and s.state not in ('HI', 'AK') and s.id != 'MWN'
  ORDER by lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
icursor.execute( sql)
for row in icursor:
    if row[4] == 0:
        continue
    lats.append( row[3] )
    lons.append( row[2] )
    vals.append( row[4] * 1.15 )
    #valmask.append(  (row[1] in ['NJ_ASOS', 'NY_ASOS',]) )
    valmask.append( True )
if len(vals) < 5:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "29 October - ASOS/AWOS Peak Wind Speed Reports",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[mph]",
 '_valuemask'         : valmask,
 '_northeast'	: True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
        now.strftime("%Y%m%d%H%M"), )
#iemplot.postprocess(tmpfp, pqstr)
iemplot.makefeature(tmpfp)