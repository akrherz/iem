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


# Extract normals
lats = []
lons = []
vals = []
rs = coop.query("""SELECT stationid, min(low) as low from alldata
     WHERE day > '2010-11-01' 
     GROUP by stationid ORDER by low DESC""").dictresult()
for i in range(len(rs)):
  stid = rs[i]['stationid']
  lats.append( st.sts[ rs[i]['stationid'].upper() ]['lat'] )
  lons.append( st.sts[ rs[i]['stationid'].upper() ]['lon'] )
  ob = rs[i]['low']
  # Find obs
  rs2 = coop.query("""SELECT year, min(low) as loww from alldata where
        stationid = '%s' and  year < 2011 and (sday >= '1101' or sday < '0114')
        GROUP by year
        ORDER by loww ASC
        """ % (stid.lower(),)
       ).dictresult()
  for j in range(len(rs2)):
    if rs2[j]['loww'] > ob:
      break
  print "[%s] 2011 low: %s  rank: %s" % (stid, ob, j)
  vals.append( (j+1) / float(len(rs2)) * 100.0 )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2010-2011 Iowa Minimum Winter Temp Percentile",
 '_valid'             : "between 1 Nov - 14 Jan [100% Warmest]",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, "")
#iemplot.makefeature(fp)
