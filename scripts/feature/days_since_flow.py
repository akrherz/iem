# Number of days since the last 0.25 inch rainfall

import sys, os, random
import iemplot
import datetime
import mx.DateTime
now = mx.DateTime.now()
import network
nt = network.Table(("IA_DCP"))
import iemdb
HADS = iemdb.connect("hads", bypass=True)
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()

# Compute normal from the climate database
sql = """
 SELECT station, max(value) from raw2013_03 r JOIN stations s ON
 (r.station = s.id) WHERE s.network = 'IA_DCP' and 
  valid > '2013-03-09' and key = 'HGIRGZ' GROUP by station
"""

def compute(ts):
    now = datetime.date(2013,1,21)
    days = (now - ts).days
    years = int(days / 365)
    months = int((days % 365) / 30)
    return "%sy%sm" % (years, months), days

lats = []
lons = []
vals = []
hcursor.execute( sql )
for row in hcursor:
    station = row[0]
    max_flow = row[1]
    for yr in ['2013','2012','2011']:
        hcursor2.execute("""
    	SELECT max(valid) from raw"""+yr+"""
    	WHERE station = %s and value >= %s and valid < '2013-03-09'
    	""" , (station, max_flow))
        row2 = hcursor2.fetchone()
        if row2 is not None:
            break
    lbl, days = compute(row2[0])
    vals.append( "%.0f~C~%s" % (max_tmpf, days-1) )
    lats.append( nt.sts[station]['lat'] )
    lons.append( nt.sts[station]['lon'] )
    print '%5s %s %s %s' % (station, max_flow, lbl, days)

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "21 Jan 2013 Low Temperature and Days Since as Cold Temperature",
 '_valid'             : "21 Jan 2013, values in F",
#'lbTitleString'      : "[days]",
 '_showvalues'        : True,
 '_format'            : '%s',
}
# Generates tmp.ps
fp = iemplot.simple_valplot(lons, lats, vals, cfg)

#iemplot.postprocess(fp, "")
iemplot.makefeature(fp)
