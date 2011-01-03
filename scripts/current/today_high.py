# Output the 12z morning low temperature

import os, random
import iemdb
import iemplot

import mx.DateTime
now = mx.DateTime.now()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

sql = """
select station, 
  x(geom) as lon, y(geom) as lat, 
  max_tmpf as high, network
from summary_%s
WHERE day = 'TODAY' and max_tmpf > -40 
and network in ('IA_ASOS', 'AWOS', 'IL_ASOS','MO_ASOS','KS_ASOS',
    'NE_ASOS','SD_ASOS','MN_ASOS','WI_ASOS')
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
 '_title'             : "Iowa ASOS/AWOS  High Temperature",
 '_valid'             : "%s" % (now.strftime("%d %b %Y %-I:%M %p"), ),
 '_labels'            : labels
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

#pqstr = "plot ac %s summary/iowa_asos_high.png iowa_asos_high.png png" % (
#        now.strftime("%Y%m%d%H%M"), )
#iemplot.postprocess(tmpfp, '')
iemplot.makefeature(tmpfp)

