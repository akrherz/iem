"""
 Generate maps of Average Temperatures
"""

import sys
from pyiem.plot import MapPlot

import datetime
import psycopg2.extras
from pyiem.network import Table as NetworkTable

now = datetime.datetime.now()
nt = NetworkTable("IACLIMATE")
nt.sts["IA0200"]["lon"] = -93.4
nt.sts["IA5992"]["lat"] = 41.65
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)


def runYear(year):
    sql = """SELECT station, avg(high) as avg_high, avg(low) as avg_low,
           avg( (high+low)/2 ) as avg_tmp, max(day)
           from alldata_ia WHERE year = %s and station != 'IA0000' and
           high is not Null and low is not Null and substr(station,3,1) != 'C'
           GROUP by station""" % (year,)
    ccursor.execute(sql)
    # Plot Average Highs
    lats = []
    lons = []
    vals = []
    labels = []
    for row in ccursor:
        sid = row['station'].upper()
        if sid not in nt.sts:
            continue
        labels.append(sid[2:])
        lats.append(nt.sts[sid]['lat'])
        lons.append(nt.sts[sid]['lon'])
        vals.append(row['avg_high'])
        maxday = row['max']

    # ---------- Plot the points
    m = MapPlot(title="Average Daily High Temperature [F] (%s)" % (year,),
                subtitle='1 January - %s' % (maxday.strftime("%d %B"),),
                axisbg='white')
    m.plot_values(lons, lats, vals, labels=labels, labeltextsize=8,
                  labelcolor='tan')
    pqstr = "plot m %s bogus %s/summary/avg_high.png png" % (
                                        now.strftime("%Y%m%d%H%M"), year,)
    m.postprocess(pqstr=pqstr)
    m.close()

    # Plot Average Lows
    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute(sql)
    for row in ccursor:
        sid = row['station'].upper()
        if sid not in nt.sts:
            continue
        labels.append(sid[2:])
        lats.append(nt.sts[sid]['lat'])
        lons.append(nt.sts[sid]['lon'])
        vals.append(row['avg_low'])

    # ---------- Plot the points
    m = MapPlot(title="Average Daily Low Temperature [F] (%s)" % (year,),
                subtitle='1 January - %s' % (maxday.strftime("%d %B"),),
                axisbg='white')
    m.plot_values(lons, lats, vals, labels=labels, labeltextsize=8,
                  labelcolor='tan')
    pqstr = "plot m %s bogus %s/summary/avg_low.png png" % (
                                        now.strftime("%Y%m%d%H%M"), year,)
    m.postprocess(pqstr=pqstr)
    m.close()

    # Plot Average Highs
    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute(sql)
    for row in ccursor:
        sid = row['station'].upper()
        if sid not in nt.sts:
            continue
        labels.append(sid[2:])
        lats.append(nt.sts[sid]['lat'])
        lons.append(nt.sts[sid]['lon'])
        vals.append(row['avg_tmp'])

    # ---------- Plot the points
    m = MapPlot(title="Average Daily Temperature [F] (%s)" % (year,),
                subtitle='1 January - %s' % (maxday.strftime("%d %B"),),
                axisbg='white')
    m.plot_values(lons, lats, vals, labels=labels, labeltextsize=8,
                  labelcolor='tan')
    pqstr = "plot m %s bogus %s/summary/avg_temp.png png" % (
                                        now.strftime("%Y%m%d%H%M"), year,)
    m.postprocess(pqstr=pqstr)
    m.close()


if __name__ == '__main__':
    runYear(sys.argv[1])
