# Generate analysis of Peak Wind Gust

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
select s.station, s.network,
  x(s.geom) as lon, y(s.geom) as lat, 
  case when s.max_sknt > s.max_gust then s.max_sknt else s.max_gust END  as wind
from summary_%s s, current c
WHERE s.station = c.station and c.valid > 'TODAY' and s.day = 'TODAY'
and s.network = c.network
and (s.network ~* 'ASOS' or s.network = 'AWOS') and s.network != 'IQ_ASOS'
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
    vals.append( row[4] * 1.16 )
    valmask.append(  (row[1] in ['AWOS','IA_ASOS']) )

if len(vals) < 5:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa ASOS/AWOS Peak Wind Speed Reports",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[mph]",
 '_valuemask'         : valmask,
# '_midwest'	: True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
        now.strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
