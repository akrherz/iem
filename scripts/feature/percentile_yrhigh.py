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
rs = iem.query("""SELECT station, max(max_tmpf) as high from summary_2010
     WHERE day > '2010-01-01' and network in ('IA_ASOS', 'AWOS') and
     max_tmpf > -30   GROUP by station
     ORDER by high ASC""").dictresult()
for i in range(len(rs)):
  stid = rs[i]['station']
  lats.append( xref[ rs[i]['station'].upper() ]['lat'] )
  lons.append( xref[ rs[i]['station'].upper() ]['lon'] )
  ob = rs[i]['high']
  cid = xref[ stid ]['climate_site']
  # Find obs
  rs2 = coop.query("""SELECT year, max(high) as highw from alldata where
        stationid = '%s' and sday < '0525' GROUP by year
        ORDER by highw ASC
        """ % (cid.lower(),)
       ).dictresult()
  for j in range(len(rs2)):
    if rs2[j]['highw'] > ob:
      break
  print "[%s] 2010 high: %s  rank: %s" % (stid, ob, j)
  vals.append( (j+1) / float(len(rs2)) * 100.0 )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2010 Iowa Maximum Temperature Percentile",
 '_valid'             : "between 1 Jan - 24 May [100% Warmest]",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, "")
