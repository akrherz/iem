# Generate a map of this month's observed precip

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
access = i['iem']

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
rs = access.query(sql).dictresult()
for i in range(len(rs)):
  id = rs[i]['id']
  labels.append( id )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )
  precip.append( rs[i]['precip'] )


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
