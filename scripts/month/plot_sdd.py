# Generate a plot of SDD 

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
   sum(sdd86(high, low)) as sdd
   from alldata_ia WHERE year = %s and month = %s
   GROUP by station""" % (now.year, now.month)

lats = []
lons = []
sdd86 = []
valmask = []
ccursor.execute( sql )
for row in ccursor:
  lats.append( nt.sts[row[0]]['lat'] )
  lons.append( nt.sts[row[0]]['lon'] )
  sdd86.append( row[1] )
  valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_valueMask'         : valmask,
 '_format'            : '%.0f',
 '_title'             : "Iowa %s SDD Accumulation" % (
                        now.strftime("%B %Y"), ),
 'lbTitleString'      : "[base 86]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, sdd86, cfg)

pqstr = "plot c 000000000000 summary/sdd_mon.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
