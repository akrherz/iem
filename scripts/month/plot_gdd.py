# Generate a plot of GDD 

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
mesosite = i['mesosite']

import network
nt = network.Table("IACLIMATE")


# Compute normal from the climate database
sql = """SELECT station,
   sum(gdd50(high, low)) as gdd
   from alldata_ia WHERE year = %s and month = %s
   GROUP by station""" % (now.year, now.month)

lats = []
lons = []
gdd50 = []
valmask = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
  if not nt.sts.has_key(rs[i]['station'].upper()):
    continue
  lats.append( nt.sts[rs[i]['station'].upper()]['lat'] )
  lons.append( nt.sts[rs[i]['station'].upper()]['lon'] )
  gdd50.append( rs[i]['gdd'] )
  valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_valueMask'         : valmask,
 '_format'            : '%.0f',
 '_title'             : "Iowa %s GDD Accumulation" % (
                        now.strftime("%B %Y"), ),
 'lbTitleString'      : "[base 50]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)

pqstr = "plot c 000000000000 summary/gdd_mon.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
