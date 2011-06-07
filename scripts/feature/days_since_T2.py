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
SELECT c.name, c.network, station, max_tmpf, x(s.geom) as lon, y(s.geom) as lat, c.climate_site from summary_2011 s, stations c where s.station = c.id 
and ((s.day = '2011-06-06' and s.network in ('IA_ASOS', 'AWOS')) or (s.day = '2011-06-07' and s.network in ('IA_COOP')))and max_tmpf > 50 and c.network = s.network
ORDER by station  ASC
"""

lats = []
lons = []
vals = []
rs = iem.query(sql).dictresult()
for i in range(len(rs)):
    station = rs[i]['station']
    max_tmpf = rs[i]['max_tmpf']
    cid = rs[i]['climate_site']
    rs2 = coop.query("""
    SELECT max(day) as maxday from alldata where high >= %s and stationid = '%s' and day < '2011-06-06'
    """ % (int(max_tmpf), cid.lower())).dictresult()

    ts = mx.DateTime.strptime(rs2[0]['maxday'], '%Y-%m-%d')
    lats.append( rs[i]['lat'] + (0.0001 * i))
    lons.append( rs[i]['lon'] )
    print '%5s %4s %-20s %3i  %s' % (station, rs[i]['network'][-4:], rs[i]['name'], max_tmpf, ts.strftime('%d %b %Y'))
    if ts.year == 2011:
        vals.append("+")
    else:
        vals.append( ts.year )

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
