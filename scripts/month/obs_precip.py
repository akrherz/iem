# Generate a map of this month's observed precip

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """SELECT id,
      sum(CASE WHEN pday < 0 THEN 0 ELSE pday END) as precip,
      x(geom) as lon, y(geom) as lat from summary_%s s, stations t
     WHERE t.network in ('IA_ASOS', 'AWOS') and
      extract(month from day) = %s and extract(year from day) = extract(year from now())
     and t.iemid = s.iemid GROUP by id, lat, lon""" % (
  now.year, now.strftime("%m"),)

lats = []
lons = []
precip = []
labels = []
icursor.execute(sql)
for row in icursor:
  id = row[0]
  labels.append( id )
  lats.append( row[3] )
  lons.append( row[2] )
  precip.append( row[1] )


#---------- Plot the points

cfg = {
 'wkColorMap': 'gsltod',
 '_format': '%.2f',
 '_labels': labels,
 '_title'       : "This Month's Precipitation [inch]",
 '_valid'       : now.strftime("%b %Y"),
}


tmpfp = iemplot.simple_valplot(lons, lats, precip, cfg)

pqstr = "plot c 000000000000 summary/month_prec.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
#iemplot.makefeature(tmpfp)
