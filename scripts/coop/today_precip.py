# Plot the COOP Precipitation Reports, don't use lame-o x100

import iemplot
import datetime

import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

sql = """
select id, 
  x(s.geom) as lon, y(s.geom) as lat, 
  pday 
from summary c, stations s
WHERE day = 'TODAY' and pday >= 0 and pday < 20
and s.network = 'IA_COOP' and s.iemid = c.iemid
"""

def n(val):
    if val == 0.001:
        return 'T'
    if val == 0:
        return '0'
    return '%.2f' % (val,)

lats = []
lons = []
vals = []
valmask = []
labels = []
icursor.execute(sql)
for row in icursor:
    lats.append( row['lat'] )
    lons.append( row['lon'] )
    vals.append( n(row['pday']) )
    labels.append( row['id'] )
    valmask.append( True )


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_showvalues'        : True,
 '_format'            : '%s',
 '_title'             : "Iowa COOP 24 Hour Precipitation",
 '_valid'             : "ending approximately %s 7 AM" % (
                            datetime.datetime.now().strftime("%-d %b %Y"), ),
# '_labels'            : labels
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot ac %s iowa_coop_precip.png iowa_coop_precip.png png" % (
        datetime.datetime.now().strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
