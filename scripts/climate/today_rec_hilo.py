# Generate a map of today's record high and low temperature

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
sql = """SELECT station, max_high, min_low from climate WHERE valid = '2000-%s'""" % (
  now.strftime("%m-%d"),)

lats = []
lons = []
highs = []
lows = []
labels = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
  id = rs[i]['station'].upper()
  labels.append( id[2:] )
  lats.append( st.sts[id]['lat'] )
  lons.append( st.sts[id]['lon'] )
  highs.append( rs[i]['max_high'] )
  lows.append( rs[i]['min_low'] )


#---------- Plot the points

cfg = {
 'wkColorMap': 'gsltod',
 '_format': '%.0f',
# '_labels': labels,
 '_title'       : "Record High + Low Temperature [F] (1893-2008)",
 '_valid'       : now.strftime("%d %b"),
}


tmpfp = iemplot.hilo_valplot(lons, lats, highs, lows, cfg)

pqstr = "plot c 000000000000 climate/iowa_today_rec_hilo_pt.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
