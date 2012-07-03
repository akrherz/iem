# Plot the High + Low Temperatures

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=int(sys.argv[1]))

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
SELECT 
  s.id as station, max_tmpf, min_tmpf, x(s.geom) as lon, y(s.geom) as lat
FROM 
  summary_%s c, stations s
WHERE
  c.iemid = s.iemid and 
  s.network IN ('AWOS', 'IA_ASOS') and
  day = '%s'
  and max_tmpf > -50 
""" % (now.year, now.strftime("%Y-%m-%d"))

lats = []
lons = []
highs = []
lows = []
labels = []
icursor.execute(sql)
for row in icursor:
  lats.append( row[4] )
  lons.append( row[3] )
  highs.append( row[1] )
  lows.append( row[2] )
  labels.append( row[0] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa High & Low Air Temperature",
 '_valid'             : now.strftime("%d %b %Y"),
 '_labels'            : labels,
 '_format'            : '%.0f',
 'lbTitleString'      : "[F]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
tmpfp = iemplot.hilo_valplot(lons, lats, highs, lows, cfg)

if sys.argv[1] == "0":
  pqstr = "plot c 000000000000 summary/asos_hilo.png bogus png"
else:
  pqstr = "plot a %s0000 bogus hilow.gif png" % (now.strftime("%Y%m%d"), )

iemplot.postprocess(tmpfp, pqstr)
