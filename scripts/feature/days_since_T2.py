# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']
coop = i['coop']


# Compute normal from the climate database
sql = """
SELECT c.name, c.network, station, min(max_tmpf), x(s.geom) as lon, y(s.geom) as lat, c.climate_site from summary_2011 s, stations c where s.station = c.id 
and s.day in ('2011-06-06','2011-06-07','2011-06-08') and s.network in ('IA_ASOS', 'AWOS') and max_tmpf > 50 and c.network = s.network
GROUP by c.name, c.network, station, lat, lon, c.climate_site ORDER by station  ASC
"""

lats = []
lons = []
vals = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
    station = rs[i]['station']
    max_tmpf = rs[i]['min']
    cid = rs[i]['climate_site']
    rs2 = coop.query("""
    SELECT year, high from alldata where stationid = '%s' and day < '2011-06-06' ORDER by day DESC
    """ % (cid.lower(),)).dictresult()
    running = 0
    for j in range(len(rs2)):
      if rs2[j]['high'] >= max_tmpf:
        running += 1
      else:
        running = 0
      if running > 2:
        vals.append( rs2[j]['year'] )
        break

    lats.append( rs[i]['lat'] + (0.0001 * i))
    lons.append( rs[i]['lon'] )
    print '%5s %4s %-20s %3i  %s' % (station, rs[i]['network'][-4:], rs[i]['name'], max_tmpf, vals[-1])

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Year of Previous Date as Warm as 6 June 2011 (High Temperature)",
 #'_valid'             : "%s" % ( now.strftime("%d %b %Y"), ),
#'lbTitleString'      : "[days]",
 '_showvalues'        : True,
 '_format'            : '%s',
}
# Generates tmp.ps
fp = iemplot.simple_valplot(lons, lats, vals, cfg)

#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
