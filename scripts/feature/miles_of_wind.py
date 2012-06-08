# Generate analysis of Peak Wind Gust

import sys, os, random
sys.path.append("../lib/")
import iemplot
import network 
nt = network.Table(["AWOS","IA_ASOS"])

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
  select s.id, c.sknt, c.valid
  from current_log c JOIN stations s on (s.iemid = c.iemid)
  WHERE c.valid > '2012-04-15' and c.valid < '2012-04-17'
  and (s.network = 'IA_ASOS' or s.network = 'AWOS') 
  and sknt >= 0 ORDER by valid ASC
""" 

import mx.DateTime
lasttime = {}
miles = {}
for id in nt.sts.keys():
    lasttime[id] =  mx.DateTime.DateTime(2012,4,15,0,0)
    miles[id] = 0

icursor.execute( sql)
for row in icursor:
    valid = mx.DateTime.strptime(row[2].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
    diff = (valid - lasttime[row[0]]).minutes
    miles[row[0]] += diff / 60.0 * row[1] * 1.15
    lasttime[row[0]] = valid

vals = []
lats = []
lons = []
for id in nt.sts.keys():
  if miles[id] == 0:
    continue
  vals.append( miles[id] )
  lats.append( nt.sts[id]['lat'] )
  lons.append( nt.sts[id]['lon'] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_format'            : '%.0f',
 '_title'             : "Iowa ASOS/AWOS Miles of Wind Passing Station",
 '_valid'             : "15-16 April 2012",
 'lbTitleString'      : "[mph]",
# '_valuemask'         : valmask,
# '_midwest'	: True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)
#tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
#pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
#        now.strftime("%Y%m%d%H%M"), )
#iemplot.postprocess(tmpfp, pqstr)
