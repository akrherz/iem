# Generate a plot of GDD 

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
mesosite = i['mesosite']

# Now we load climatology
sts = {}
rs = mesosite.query("SELECT id, x(geom) as lon, y(geom) as lat from stations WHERE \
    network = 'IACLIMATE'").dictresult()
for i in range(len(rs)):
    sts[ rs[i]["id"].lower() ] = rs[i]


# Compute normal from the climate database
sql = """SELECT stationid,
   sum(gdd50(high, low)) as gdd
   from alldata WHERE year = %s and month in (5,6,7,8,9,10)
   GROUP by stationid""" % (now.year)

lats = []
lons = []
gdd50 = []
valmask = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
  if not sts.has_key(rs[i]['stationid']):
    continue
  lats.append( sts[rs[i]['stationid']]['lat'] )
  lons.append( sts[rs[i]['stationid']]['lon'] )
  gdd50.append( rs[i]['gdd'] )
  valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_valueMask'         : valmask,
 '_format'            : '%.0f',
 '_title'             : "Iowa 1 May - %s GDD Accumulation" % (
                        now.strftime("%d %B %Y"), ),
 'lbTitleString'      : "[base 50]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)

pqstr = "plot c 000000000000 summary/gdd_may1.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
