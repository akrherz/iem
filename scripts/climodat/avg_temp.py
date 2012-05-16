"""
 Generate maps of Average Temperatures
"""

import sys, os
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
    sql = """SELECT station, avg(high) as avg_high, avg(low) as avg_low,
           avg( (high+low)/2 ) as avg_tmp
           from alldata_ia WHERE year = %s and station != 'IA0000' and 
           high is not Null and low is not Null GROUP by station""" % (year,)
    ccursor.execute( sql )
  # Plot Average Highs
    lats = []
    lons = []
    vals = []
    labels = []
    for row in ccursor:
        id = row['station'].upper()
        if not nt.sts.has_key(id):
            continue
        labels.append( id[2:] )
        lats.append( nt.sts[id]['lat'] )
        lons.append( nt.sts[id]['lon'] )
        vals.append( row['avg_high'] )

    #---------- Plot the points

    cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.1f',
     '_labels'   : labels,
     '_valid'    : '1 Jan - %s' % (now.strftime("%d %B"),),
     '_title'    : "Average Daily High Temperature [F] (%s)" % (year,),
     }

    tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
    pqstr = "plot m %s/summary/avg_high.png" % (year,)
    iemplot.postprocess(tmpfp, pqstr)
    iemplot.simple_valplot(lons, lats, vals, cfg)


    # Plot Average Lows
    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute( sql )
    for row in ccursor:
        id = row['station'].upper()
        if not nt.sts.has_key(id):
            continue
        labels.append( id[2:] )
        lats.append( nt.sts[id]['lat'] )
        lons.append( nt.sts[id]['lon'] )
        vals.append( row['avg_low'] )

    #---------- Plot the points

    cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.1f',
     '_labels'   : labels,
     '_valid'    : '1 Jan - %s' % (now.strftime("%d %B"),),
     '_title'    : "Average Daily Low Temperature [F] (%s)" % (year,),
     }

    tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
    pqstr = "plot m %s/summary/avg_low.png" % (year,)
    iemplot.postprocess(tmpfp, pqstr)
    iemplot.simple_valplot(lons, lats, vals, cfg)

    # Plot Average Highs
    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute( sql )
    for row in ccursor:
        id = row['station'].upper()
        if not nt.sts.has_key(id):
            continue
        labels.append( id[2:] )
        lats.append( nt.sts[id]['lat'] )
        lons.append( nt.sts[id]['lon'] )
        vals.append( row['avg_tmp'] )

    #---------- Plot the points

    cfg = {
     'wkColorMap': 'gsltod',
     '_format'   : '%.1f',
     '_labels'   : labels,
     '_valid'    : '1 Jan - %s' % (now.strftime("%d %B"),),
     '_title'    : "Average Daily Temperature (mean high+low) [F] (%s)" % (year,),
  }

    tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)
    pqstr = "plot m %s/summary/avg_temp.png" % (year,)
    iemplot.postprocess(tmpfp, pqstr)
    iemplot.simple_valplot(lons, lats, vals, cfg)


if __name__ == '__main__':
    runYear( sys.argv[1] )
