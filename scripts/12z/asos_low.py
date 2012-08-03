# Output the 12z morning low temperature

import sys, os, random
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

sql = """
select s.id, 
  x(s.geom) as lon, y(s.geom) as lat, 
  min(tmpf) as low12z
 from current_log c, stations s
 WHERE tmpf > -40 and valid > '%s 00:00:00+00' and valid < '%s 12:00:00+00' 
 and s.network in ('IA_ASOS', 'AWOS') and s.iemid = c.iemid GROUP by id, lon, lat
""" % (now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))

lats = []
lons = []
vals = []
valmask = []
labels = []
icursor.execute(sql)
for row in icursor:
  lats.append( row[2] )
  lons.append( row[1] )
  vals.append( row[3] )
  labels.append( row[0] )
  valmask.append( True )

if icursor.rowcount < 5:
  sys.exit(0)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa ASOS/AWOS 12Z Morning Low Temperature",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 '_labels'            : labels
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

pqstr = "plot ac %s summary/iowa_asos_12z_low.png iowa_asos_12z_low.png png" % (
        now.strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
