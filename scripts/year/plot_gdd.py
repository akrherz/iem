# Generate a plot of GDD for the ASOS/AWOS network

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
mesosite = i['mesosite']

gfunc = "gdd50"
gbase = 50
if len(sys.argv) == 2 and sys.argv[1] == "gdd52":
  gfunc = "gdd52"
  gbase = 52

# Now we load climatology
sts = {}
rs = mesosite.query("SELECT id, x(geom) as lon, y(geom) as lat from stations WHERE \
    network = 'IACLIMATE'").dictresult()
for i in range(len(rs)):
    sts[ rs[i]["id"].lower() ] = rs[i]


# Compute normal from the climate database
sql = """SELECT stationid,
   sum(%s(high, low)) as gdd
   from alldata WHERE stationid != 'ia0000' and year = %s
   GROUP by stationid""" % (gfunc, now.year)

lats = []
lons = []
gdd50 = []
valmask = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
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
 '_title'             : "Iowa %s GDD (base=%s) Accumulation" % (
                        now.strftime("%Y"), gbase),
 '_valid'          : "1 Jan - %s" % (
                        now.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[base %s] " % (gbase,),
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)

pqstr = "plot c 000000000000 summary/gdd_jan1.png bogus png"
if gbase == 52:
  pqstr = "plot c 000000000000 summary/gdd52_jan1.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
