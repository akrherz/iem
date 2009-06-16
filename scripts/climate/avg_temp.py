# Generate a map of average temperature

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb, stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
st.sts["IA0200"]["lon"] = -93.6
st.sts["IA5992"]["lat"] = 41.65
i = iemdb.iemdb()
coop = i['coop']

# Compute normal from the climate database
sql = """SELECT station, avg( (high+low)/2.0 ) as mean
   from climate GROUP by station"""

lats = []
lons = []
vals = []
labels = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
  id = rs[i]['station'].upper()
  labels.append( id[2:] )
  lats.append( st.sts[id]['lat'] )
  lons.append( st.sts[id]['lon'] )
  vals.append( rs[i]['mean'] )


#---------- Plot the points

cfg = {
 'wkColorMap': 'gsltod',
 '_format': '%.1f',
 '_labels': labels,
 '_title'       : "Average Air Temperature [F] (1951-2008)",
}


iemplot.simple_valplot(lons, lats, vals, cfg)

os.system("convert -depth 8 -colors 128 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 tmp.ps temp.png")
#os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/gdd_norm_may1_pt.png bogus png' gdd_norm_may1_pt.png")
#os.remove("gdd_norm_may1_pt.png")
os.remove("tmp.ps")
