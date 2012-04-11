# Number of days since the last 0.25 inch rainfall

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
select id, 
  x(geom) as lon, y(geom) as lat, 
  max(day) as maxday
from summary_2012 s JOIN stations t on (t.iemid = s.iemid) 
WHERE min_tmpf < 32
and (network ~* 'ASOS' or network = 'AWOS') 
and country = 'US' 
GROUP by id, lon, lat ORDER by maxday DESC
"""

lats = []
lons = []
vals = []
icursor.execute(sql)
for row in icursor:
  ts = mx.DateTime.strptime(row[3].strftime("%Y-%m-%d"), '%Y-%m-%d')
  lats.append( row[2] )
  lons.append( row[1] )
  vals.append( (now -ts).days - 1)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_midwest' : True,
 '_title'             : "Days since sub 32 degree temperature",
 '_valid'             : "%s" % ( now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[days]",
 '_showvalues'        : False,
 '_format'            : '%.0f',
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(fp)
#iemplot.postprocess(fp, "")
