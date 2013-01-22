"""
 Generate a map of Number of days with precip
"""

import sys
import iemplot
import datetime
now = datetime.datetime.now()

import network
nt = network.Table("IACLIMATE")
nt.sts["IA0200"]["lon"] = -93.4
nt.sts["IA5992"]["lat"] = 41.65
import iemdb
import psycopg2.extras
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

def runYear(year):
    # Grab the data
    sql = """SELECT station, sum(case when precip >= 0.01 then 1 else 0 end) as days,
        max(day)
           from alldata_ia WHERE year = %s and substr(station,3,1) != 'C' 
           and station != 'IA0000' GROUP by station""" % (year,)

    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute( sql )
    for row in ccursor:
        sid = row['station'].upper()
        if not nt.sts.has_key(sid):
            continue
        labels.append( sid[2:] )
        lats.append( nt.sts[sid]['lat'] )
        lons.append( nt.sts[sid]['lon'] )
        vals.append( row['days'] )
        maxday = row['max']

    #---------- Plot the points

    cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.0f',
     '_labels'   : labels,
     '_valid'    : '1 January - %s' % (maxday.strftime("%d %B"),),
     '_title'    : "Days with Measurable Precipitation (%s)" % (year,),
  }

    tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
    pqstr = "plot m %s bogus %s/summary/precip_days.png png" % (
                                        now.strftime("%Y%m%d%H%M"), year,)
    iemplot.postprocess(tmpfp, pqstr)
    iemplot.simple_valplot(lons, lats, vals, cfg)

if __name__ == '__main__':
    runYear( sys.argv[1] )
