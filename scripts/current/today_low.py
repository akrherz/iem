# Output the 12z morning low temperature

import os, random
import iemdb
import iemplot

import mx.DateTime
now = mx.DateTime.now()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

sql = """
select c.station, 
  x(s.geom) as lon, y(s.geom) as lat, 
  min_tmpf as low, s.network
 from summary_%s c, stations s
 WHERE day = 'TODAY' and min_tmpf < 90 
 and (c.network ~* 'ASOS' or c.network ~* 'AWOS' or c.network = 'IA_COOP') 
 and s.country = 'US' and s.network = c.network and s.id = c.station 
""" % (now.year, )

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
  valmask.append( row[4] in ['AWOS', 'IA_ASOS'] )


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_showvalues'        : True,
 '_valuemask'         :   valmask,
 'lbTitleString'    : 'F',
 '_format'            : '%.0f',
 '_title'             : "Iowa Morning Low Temperature",
 '_valid'             : "%s" % (now.strftime("%d %b %Y"), ),
 '_labels'            : labels,
# '_midwest'		: True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s summary/iowa_asos_high.png iowa_asos_high.png png" % (
        now.strftime("%Y%m%d%H%M"), )
iemplot.postprocess(tmpfp, pqstr)
#iemplot.makefeature(tmpfp)

