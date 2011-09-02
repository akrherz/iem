# Generate a map of today's record high and low temperature

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import network
nt = network.Table('IACLIMATE')
nt.sts["IA0200"]["lon"] = -93.6
nt.sts["IA5992"]["lat"] = 41.65
import iemdb
import psycopg2.extras
coop = iemdb.connect('coop', bypass=True)

# Compute normal from the climate database
sql = """SELECT station, max_high, min_low from climate WHERE valid = '2000-%s'
    and substr(station,0,3) = 'ia'""" % (
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
  lats.append( nt.sts[id]['lat'] )
  lons.append( nt.sts[id]['lon'] )
  highs.append( row['max_high'] )
  lows.append( row['min_low'] )


#---------- Plot the points

cfg = {
 'wkColorMap': 'gsltod',
 '_format': '%.0f',
# '_labels': labels,
 '_title'       : "Record High + Low Temperature [F] (1893-2008)",
 '_valid'       : now.strftime("%d %b"),
}


tmpfp = iemplot.hilo_valplot(lons, lats, highs, lows, cfg)

pqstr = "plot ac %s0000 climate/iowa_today_rec_hilo_pt.png coop_rec_temp.png png" % (now.strftime("%Y%m%d"),)
iemplot.postprocess(tmpfp, pqstr)
