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
wepp = i['wepp']

# Extract normals
lats = []
lons = []
vals = []
rs = coop.query("""SELECT stationid, sum(precip) as rain from alldata
     WHERE month in (6,7) and year = 2010 and 
     stationid != 'ia0000' GROUP by stationid""").dictresult()
for i in range(len(rs)):
  stid = rs[i]['stationid']
  lats.append( st.sts[ rs[i]['stationid'].upper() ]['lat'] )
  lons.append( st.sts[ rs[i]['stationid'].upper() ]['lon'] )
  obs = rs[i]['rain'] 
  # Find obs
  rs2 = coop.query("""SELECT year, sum(precip) as rain from alldata where
        stationid = '%s' and month IN (6,7) GROUP by year ORDER by rain ASC""" % (stid,)
       ).dictresult()
  for j in range(len(rs2)):
    if rs2[j]['rain'] > obs:
      break
  vals.append( (j+1) / float(len(rs2)) * 100.0 )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Jun/Jul Rainfall Percentile",
 '_valid'             : "1 Jun - 31 Jul 2010",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, "")
