# Month percentile 

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb, stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
i = iemdb.iemdb()
coop = i['coop']
iem = i['iem']
mesosite = i['mesosite']

xref = {}
rs = mesosite.query("SELECT id, climate_site, x(geom) as lon, y(geom) as lat from stations WHERE network in ('IA_ASOS', 'AWOS')").dictresult()
for i in range(len(rs)):
  xref[ rs[i]['id'] ] = rs[i]


# Extract normals
lats = []
lons = []
vals = []
rs = iem.query("""SELECT station, max(max_tmpf) as low from summary_2010
     WHERE day > '2010-01-01' and network in ('IA_ASOS', 'AWOS') and
     max_tmpf > 40 and station not in ('CKP') GROUP by station""").dictresult()
for i in range(len(rs)):
  stid = rs[i]['station']
  lats.append( xref[ rs[i]['station'].upper() ]['lat'] )
  lons.append( xref[ rs[i]['station'].upper() ]['lon'] )
  ob = rs[i]['low']
  cid = xref[ stid ]['climate_site']
  # Find obs
  rs2 = coop.query("""SELECT year, max(high) as highm from alldata where
        stationid = '%s' and sday < '0329' GROUP by year
        ORDER by highm ASC
        """ % (cid.lower(),)
       ).dictresult()
  for j in range(len(rs2)):
    if rs2[j]['highm'] > ob:
      break
  print "[%s] 2010 high: %s  rank: %s" % (stid, ob, j)
  vals.append( (j+1) / float(len(rs2)) * 100.0 )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2010 Iowa Maximum Temperature Percentile",
 '_valid'             : "between 1 Jan - 29 Mar [100% Warmest]",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage %s.ps %s.png" % (fp,fp))
if os.environ['USER'] == 'akrherz':
  os.system("xv %s.png" % (fp,))
  sys.exit()
os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 320x210 -density 120 +repage tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 lsr_snowfall_thumb.png bogus png' tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")

