# Generate a map of today's record high and low temperature

import sys, os
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import network
nt = network.Table('IACLIMATE')
st.sts["IA0200"]["lon"] = -93.6
st.sts["IA5992"]["lat"] = 41.65
i = iemdb.iemdb()
coop = i['coop']

# Compute normal from the climate database
sql = """SELECT station, min_high, min_low from climate WHERE valid = '2000-%s'
    and substr(station,0,3) = 'ia'""" % (
  now.strftime("%m-%d"),)

lats = []
lons = []
highs = []
lows = []
labels = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
  id = rs[i]['station'].upper()
  labels.append( id[2:] )
  lats.append( st.sts[id]['lat'] )
  lons.append( st.sts[id]['lon'] )
  highs.append( rs[i]['min_high'] )
  lows.append( rs[i]['min_low'] )


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
