# Generate a plot of GDD for the ASOS/AWOS network

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

import network
st = network.Table('IACLIMATE')
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


gfunc = "gdd50"
gbase = 50
if len(sys.argv) == 2 and sys.argv[1] == "gdd52":
  gfunc = "gdd52"
  gbase = 52
if len(sys.argv) == 2 and sys.argv[1] == "gdd48":
  gfunc = "gdd48"
  gbase = 48

# Compute normal from the climate database
ccursor.execute("""SELECT station,
   sum(%s(high, low)) as gdd
   from alldata_ia WHERE station != 'ia0000' and year = %s
   GROUP by station""" % (gfunc, now.year))

lats = []
lons = []
gdd50 = []
valmask = []

for row in ccursor:
    station = row[0]
    if not st.sts.has_key(station):
        continue
    lats.append( st.sts[station]['lat'] )
    lons.append( st.sts[station]['lon'] )
    gdd50.append( row[1] )
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
elif gbase == 48:
  pqstr = "plot c 000000000000 summary/gdd48_jan1.png bogus png"
iemplot.postprocess(tmpfp, pqstr)