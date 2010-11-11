# Month percentile 

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb, stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
i = iemdb.iemdb()
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
rs = iem.query("""SELECT station, max_tmpf from summary_2010
     WHERE day = '2010-04-01' and network in ('IA_ASOS', 'AWOS') and
     max_tmpf > 40 and station not in ('AXA','MXO','BNW','CWI','CKP','I75','CNC') """).dictresult()
for i in range(len(rs)):
  stid = rs[i]['station']
  lats.append( xref[ rs[i]['station'].upper() ]['lat'] )
  lons.append( xref[ rs[i]['station'].upper() ]['lon'] )
  ob = rs[i]['max_tmpf']
  # Find obs
  rs2 = iem.query("""SELECT count(*) as days from summary_2009 where
        station = '%s' and max_tmpf > %s 
        """ % (stid, ob)
       ).dictresult()
  print "[%s] 2010 high: %s  rank: %s" % (stid, ob, rs2[0]['days'])
  vals.append( float(rs2[0]['days']) )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Days in 2009 warmer than 1 Apr 2010",
 '_valid'             : "",
 'lbTitleString'      : "[days]",
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
