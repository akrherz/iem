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
 SELECT c.name, c.network, c.id, max_tmpf, x(c.geom) as lon, 
 y(c.geom) as lat, c.climate_site from summary_2013 s, stations c 
 where s.iemid = c.iemid
 and s.day = '2013-05-14' and c.network in ('IA_ASOS', 'AWOS') 
 and max_tmpf > 0 and id not in ('xxx')
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
    and high >= %.0f and day < '2013-05-14'
    """ % (cid, max_tmpf))
    row2 = ccursor.fetchone()
    if row2[0] is None:
       continue
    lbl, days = compute(row2[0])
    vals.append( "%.0f~C~%s" % (max_tmpf, lbl) )
    lats.append( row[5] )
    lons.append( row[4] )
    print '%5s %s %s %s' % (station, max_tmpf, lbl, days)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "14 May 2013 High Temperature and Days Since as High Temp",
 '_valid'             : "14 May 2013, values in F",
#'lbTitleString'      : "[days]",
 '_showvalues'        : True,
 '_format'            : '%s',
}
# Generates tmp.ps
fp = iemplot.simple_valplot(lons, lats, vals, cfg)

#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
