# Generate a plot of normal GDD Accumulation since 1 May of this year

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()
if now.month < 5 or now.month > 10:
  sys.exit(0)

from pyIEM import iemdb, stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
i = iemdb.iemdb()
coop = i['coop']

# Compute normal from the climate database
sql = """SELECT station, sum(gdd50) as gdd, sum(sdd86) as sdd 
   from climate WHERE gdd50 IS NOT NULL and sdd86 IS NOT NULL and 
   valid >= '2000-05-01' and valid <=
  ('2000-'||to_char(CURRENT_TIMESTAMP, 'mm-dd'))::date GROUP by station"""

lats = []
lons = []
gdd50 = []
sdd86 = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
  id = rs[i]['station'].upper()
  lats.append( st.sts[id]['lat'] )
  lons.append( st.sts[id]['lon'] )
  gdd50.append( rs[i]['gdd'] )
  sdd86.append( rs[i]['sdd'] )


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 'tiMainString'       : "1 May - %s Average GDD Accumulation" % (
                        now.strftime("%d %b"), ),
 'lbTitleString'      : "[base 50]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, gdd50, cfg)

os.system("convert -rotate -90 tmp.ps gdd_norm_may1.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/gdd_norm_may1.png bogus png' gdd_norm_may1.png")
os.remove("gdd_norm_may1.png")
os.remove("tmp.ps")

#---------- Plot the points

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_format': '%.0f',
 'tiMainString'       : "1 May - %s Average GDD Accumulation" % (
                        now.strftime("%d %b"), ),
}


iemplot.simple_valplot(lons, lats, gdd50, cfg)

os.system("convert -rotate -90 tmp.ps gdd_norm_may1_pt.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/gdd_norm_may1_pt.png bogus png' gdd_norm_may1_pt.png")
os.remove("gdd_norm_may1_pt.png")
os.remove("tmp.ps")




