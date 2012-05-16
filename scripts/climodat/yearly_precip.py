"""
Generate a map of Yearly Precipitation
"""

import sys
import os
import iemplot
import mx.DateTime
now = mx.DateTime.now()

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
    sql = """SELECT station, sum(precip) as total
           from alldata_ia WHERE year = %s and
           station != 'IA0000' GROUP by station""" % (year,)

    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute( sql )
    for row in ccursor:
        if row['total'] < 10: # Arb Threshold
            continue
        id = row['station'].upper()
        if not nt.sts.has_key(id):
            continue
        labels.append( id[2:] )
        lats.append( nt.sts[id]['lat'] )
        lons.append( nt.sts[id]['lon'] )
        vals.append( row['total'] )

    #---------- Plot the points

    cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.2f',
     '_labels'   : labels,
     '_valid'    : '1 Jan - %s' % (now.strftime("%d %B"),),
     '_title'    : "Total Precipitation [inch] (%s)" % (year,),
     }

    tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
    pqstr = "plot m %s/summary/total_precip.png" % (year,)
    iemplot.postprocess(tmpfp, pqstr)


if __name__ == '__main__':
    runYear( sys.argv[1] )
