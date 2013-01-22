"""
Generate a map of Yearly Precipitation
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
    sql = """SELECT station, sum(precip) as total, max(day)
           from alldata_ia WHERE year = %s and
           station != 'IA0000' and
           substr(station,3,1) != 'C' GROUP by station""" % (year,)

    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute( sql )
    for row in ccursor:
        sid = row['station']
        if not nt.sts.has_key(sid):
            continue
        labels.append( sid[2:] )
        lats.append( nt.sts[sid]['lat'] )
        lons.append( nt.sts[sid]['lon'] )
        vals.append( row['total'] )
        maxday = row['max']

    #---------- Plot the points

    cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.2f',
     '_labels'   : labels,
     '_valid'    : '1 January - %s' % (maxday.strftime("%d %B"),),
     '_title'    : "Total Precipitation [inch] (%s)" % (year,),
     }

    tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
    pqstr = "plot m %s bogus %s/summary/total_precip.png png" % (
                                        now.strftime("%Y%m%d%H%M"), year,)
    iemplot.postprocess(tmpfp, pqstr)


if __name__ == '__main__':
    runYear( sys.argv[1] )
