# Month percentile 

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import network
nt = network.Table("IACLIMATE")
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()


# Extract normals
lats = []
lons = []
vals = []
ccursor.execute("""SELECT station, min(low) as low from alldata_ia
     WHERE day > '2011-09-01' and station != 'IA4705'
     GROUP by station ORDER by low DESC""")
for row in ccursor:
  stid = row[0]
  lats.append( nt.sts[ stid ]['lat'] )
  lons.append( nt.sts[ stid ]['lon'] )
  ob = row[1]
  # Find obs
  ccursor2.execute("""SELECT year, min(low) as loww from alldata_ia where
        station = '%s' and  year < 2011 and sday >= '0901' and sday < '1018'
        GROUP by year
        ORDER by loww ASC
        """ % (stid,)
       )
  j = 0
  for row2 in ccursor2:
    if row2[1] > ob:
      break
    j += 1
  rank = float(j+1) / (float(ccursor2.rowcount) +1 )* 100.0
  print "[%s] 2011 low: %s rank: %.1f" % (stid, ob, rank)
  vals.append( rank )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2011 Iowa Minimum Fall Temp Percentile",
 '_valid'             : "between 1 Sep - 17 Oct [100% Warmest]",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
