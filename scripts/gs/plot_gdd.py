# Generate a plot of GDD 

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import network
nt = network.Table("IACLIMATE")



# Compute normal from the climate database
sql = """SELECT station,
   sum(gdd50(high, low)) as gdd
   from alldata WHERE year = %s and month in (5,6,7,8,9,10)
   GROUP by station""" % (now.year)

lats = []
lons = []
gdd50 = []
valmask = []
ccursor.execute( sql )
for row in ccursor:
  if not nt.sts.has_key(row[0]):
    continue
  lats.append( nt.sts[row[0]]['lat'] )
  lons.append( nt.sts[row[0]]['lon'] )
  gdd50.append( row[1] )
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
