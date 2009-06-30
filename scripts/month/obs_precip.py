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
sql = """SELECT station,
      sum(CASE WHEN pday < 0 THEN 0 ELSE pday END) as precip,
      x(geom) as lon, y(geom) as lat from summary 
     WHERE network in ('IA_ASOS', 'AWOS') and
      extract(month from day) = %s 
     and station != 'TVK' GROUP by station, lat, lon""" % (
  now.strftime("%m"),)

lats = []
lons = []
precip = []
labels = []
rs = access.query(sql).dictresult()
for i in range(len(rs)):
  id = rs[i]['station']
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


iemplot.simple_valplot(lons, lats, precip, cfg)

os.system("convert -depth 8 -colors 128 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/month_prec.png bogus png' tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
