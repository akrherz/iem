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
 SELECT c.name, c.network, c.id, pday, x(c.geom) as lon, 
 y(c.geom) as lat, c.climate_site from summary_2013 s, stations c 
 where s.iemid = c.iemid
 and s.day = '2013-04-17' and c.network in ('IA_ASOS', 'AWOS') 
 and pday > 0 and id not in ('OXV', 'OOA', 'IKV', 'BRL', 'GGI')
 ORDER by id ASC
"""

def compute(ts):
    now = datetime.date(2013,4,17)
    days = (now - ts).days
    years = int(days / 365)
    months = int((days % 365) / 30)
    if years == 0 and months == 0 and days == 1:
        return '-', 0
    if years == 0 and months == 0:
        return "%sd" % (days,), days
    if years == 0:
        return "%sm" % (months,), days
    return "%sy%sm" % (years, months), days

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
    and precip >= %.0f and day < '2013-04-17'
    """ % (cid, max_tmpf))
    row2 = ccursor.fetchone()
    lbl, days = compute(row2[0])
    vals.append( "%.2f~C~%s" % (max_tmpf, lbl) )
    lats.append( row[5] )
    lons.append( row[4] )
    print '%5s %s %s %s' % (station, max_tmpf, lbl, days)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "17 Apr 2013 Precipitation and Days Since as High Amount",
 '_valid'             : "17 Apr 2013, values in inch",
#'lbTitleString'      : "[days]",
 '_showvalues'        : True,
 '_format'            : '%s',
}
# Generates tmp.ps
fp = iemplot.simple_valplot(lons, lats, vals, cfg)

#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
