# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect("iem", bypass=True)
COOP = iemdb.connect("coop", bypass=True)
icursor = IEM.cursor()
ccursor = COOP.cursor()

# Compute normal from the climate database
sql = """
 SELECT c.name, c.network, c.id, max_tmpf - min_tmpf, x(c.geom) as lon, 
 y(c.geom) as lat, c.climate_site from summary_2012 s, stations c where s.iemid = c.iemid
 and s.day = '2012-09-24' and c.network in ('IA_ASOS', 'AWOS') 
 ORDER by id ASC
"""

lats = []
lons = []
vals = []
icursor.execute( sql )
for row in icursor:
    station = row[2]
    ts = mx.DateTime.strptime('20120924', "%Y%m%d")
    max_tmpf = row[3]
    cid = row[6]
    ccursor.execute("""
    SELECT max(day) from alldata_ia where station = '%s' 
    and high - low >= %.0f
    """ % (cid, max_tmpf))
    running = 0
    row2 = ccursor.fetchone()
    ts2 = mx.DateTime.strptime(row2[0].strftime("%Y%m%d"), "%Y%m%d")
    vals.append( "%.0f~C~%s" % (max_tmpf, ts2.year,) )
    lats.append( row[5] )
    lons.append( row[4] )
    print '%5s %s' % (station, max_tmpf)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Amount/Year of Previous Date with as Large Hi-Lo Diff",
 '_valid'             : "since temperature change on 24 September 2012, values in F",
#'lbTitleString'      : "[days]",
 '_showvalues'        : True,
 '_format'            : '%s',
}
# Generates tmp.ps
fp = iemplot.simple_valplot(lons, lats, vals, cfg)

#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
