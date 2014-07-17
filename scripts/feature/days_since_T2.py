# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot
import datetime
import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect("iem", bypass=True)
COOP = iemdb.connect("coop", bypass=True)
icursor = IEM.cursor()
ccursor = COOP.cursor()

# Compute normal from the climate database
sql = """
 SELECT c.name, c.network, c.id, min(min_tmpf), ST_x(c.geom) as lon, 
 ST_y(c.geom) as lat, c.climate_site from summary_2014 s, stations c 
 where s.iemid = c.iemid
 and s.day in ('2014-07-15', '2014-07-14') and c.network in ('IA_ASOS', 'AWOS') 
 and min_tmpf < 90 GROUP by name, network, id, lon, lat, climate_site
 ORDER by id ASC
"""

def compute(ts):
    now = datetime.date(2014,7,15)
    days = (now - ts).days
    years = int(days / 365)
    months = int((days % 365) / 30)
    if years == 0 and months == 0 and days == 1:
        return '-', 0
    if years == 0 and months == 0:
        return "%sd" % (days,), days
    if years == 0:
        return "%sm" % (months,), days
    return "%sy" % (years,), days

lats = []
lons = []
vals = []
icursor.execute( sql )
for row in icursor:
    station = row[2]
    max_tmpf = row[3]
    cid = row[6]
    ccursor.execute("""
    SELECT max(day) from alldata_ia where station = '%s' 
    and low <= %.0f and year < 2014 and month = 7
    """ % (cid, max_tmpf))
    row2 = ccursor.fetchone()
    if row2[0] is None:
        continue
    lbl, days = compute(row2[0])
    #vals.append( "%.0f~C~%s" % (max_tmpf, lbl) )
    vals.append( "%.0f" % (max_tmpf,) )
    lats.append( row[5] )
    lons.append( row[4] )
    print '%5s %s %s %s %s %s' % (station, max_tmpf, lbl, days, cid, row2[0])

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "15-16 July 2014 Coldest Temperature",
 '_valid'             : "based on Iowa ASOS/AWOS Data",
#'lbTitleString'      : "[days]",
 '_showvalues'        : True,
 '_format'            : '%s',
}
# Generates tmp.ps
fp = iemplot.simple_valplot(lons, lats, vals, cfg)

#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
