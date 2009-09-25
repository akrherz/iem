# Plot the High + Low Temperatures

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=int(sys.argv[1]))

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

# Compute normal from the climate database
sql = """
SELECT 
  station, max_tmpf, min_tmpf, x(geom) as lon, y(geom) as lat
FROM 
  summary
WHERE
  network IN ('AWOS', 'IA_ASOS') and
  day = '%s'
  and max_tmpf > -50 
""" % (now.strftime("%Y-%m-%d"),)

lats = []
lons = []
highs = []
lows = []
labels = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  highs.append( rs[i]['max_tmpf'] )
  lows.append( rs[i]['min_tmpf'] )
  labels.append( rs[i]['station'] )

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
iemplot.hilo_valplot(lons, lats, highs, lows, cfg)

os.system("convert -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
if sys.argv[1] == "0":
  os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/asos_hilo.png bogus png' tmp.png")
else:
  os.system("/home/ldm/bin/pqinsert -p 'plot a %s0000 bogus hilow.gif png' tmp.png" % (now.strftime("%Y%m%d"),))
if os.environ['USER'] == 'akrherz':
  os.system("xv tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
