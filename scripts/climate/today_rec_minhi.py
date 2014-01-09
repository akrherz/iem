# Generate a map of today's record high and low temperature

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import network
nt = network.Table('IACLIMATE')
nt.sts["IA0200"]["lon"] = -93.6
nt.sts["IA5992"]["lat"] = 41.65
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# Compute normal from the climate database
sql = """SELECT station, min_high, min_low from climate WHERE valid = '2000-%s'
    and substr(station,0,3) = 'IA'""" % (
  now.strftime("%m-%d"),)

lats = []
lons = []
highs = []
lows = []
labels = []
ccursor.execute(sql)
for row in ccursor:
    sid = row[0]
    if sid[2] == 'C' or sid[2:] == '0000' or not nt.sts.has_key(sid):
        continue
    labels.append( sid[2:] )
    lats.append( nt.sts[sid]['lat'] )
    lons.append( nt.sts[sid]['lon'] )
    highs.append( row[1] )
    lows.append( row[2] )


#---------- Plot the points

cfg = {
'wkColorMap': 'BlAqGrYeOrRe',
 '_format': '%.0f',
 '_showvalues': True,
# '_labels': labels,
 '_title'       : "Record Minimum High Temperature [F] (1893-2008)",
 '_valid'       : now.strftime("%d %b"),
 'lbTitleString' : '[F]',
}


tmpfp = iemplot.simple_contour(lons, lats, highs, cfg)
pqstr = "plot c 000000000000 climate/iowa_today_rec_minhi.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
