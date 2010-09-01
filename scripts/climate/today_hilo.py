# Generate a map of today's average high and low temperature

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
st.sts["IA0200"]["lon"] = -93.6
st.sts["IA5992"]["lat"] = 41.65
import iemdb
import psycopg2.extras
coop = iemdb.connect('coop', bypass=True)

# Compute normal from the climate database
sql = """SELECT station, high, low from climate WHERE valid = '2000-%s'""" % (
  now.strftime("%m-%d"),)

lats = []
lons = []
highs = []
lows = []
labels = []
c = coop.cursor(cursor_factory=psycopg2.extras.DictCursor)
c.execute(sql)
for row in c:
  id = row['station'].upper()
  labels.append( id[2:] )
  lats.append( st.sts[id]['lat'] )
  lons.append( st.sts[id]['lon'] )
  highs.append( row['high'] )
  lows.append( row['low'] )


#---------- Plot the points

cfg = {
 'wkColorMap': 'gsltod',
 '_format': '%.0f',
# '_labels': labels,
 '_title'       : "Average High + Low Temperature [F] (1893-2008)",
 '_valid'       : now.strftime("%d %b"),
}


tmpfp = iemplot.hilo_valplot(lons, lats, highs, lows, cfg)

pqstr = "plot ac %s0000 climate/iowa_today_avg_hilo_pt.png coop_avg_temp.png png" % (
  now.strftime("%Y%m%d"), )
iemplot.postprocess(tmpfp, pqstr)
