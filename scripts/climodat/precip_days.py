"""
 Generate a map of Number of days with precip
"""

import sys
from pyiem.plot import MapPlot
import datetime

from pyiem.network import Table as NetworkTable
import psycopg2.extras
now = datetime.datetime.now()
nt = NetworkTable("IACLIMATE")
nt.sts["IA0200"]["lon"] = -93.4
nt.sts["IA5992"]["lat"] = 41.65
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)


def runYear(year):
    # Grab the data
    sql = """SELECT station,
        sum(case when precip >= 0.01 then 1 else 0 end) as days, max(day)
        from alldata_ia WHERE year = %s and substr(station,3,1) != 'C'
        and station != 'IA0000' GROUP by station""" % (year,)

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
        vals.append(row['days'])
        maxday = row['max']

    m = MapPlot(title="Days with Measurable Precipitation (%s)" % (year,),
                subtitle='Map valid January 1 - %s' % (
                                                maxday.strftime("%b %d")),
                axisbg='white')
    m.plot_values(lons, lats, vals, fmt='%.0f', labels=labels,
                  labeltextsize=8, labelcolor='tan')
    m.drawcounties()
    pqstr = "plot m %s bogus %s/summary/precip_days.png png" % (
                                        now.strftime("%Y%m%d%H%M"), year,)
    m.postprocess(pqstr=pqstr)

if __name__ == '__main__':
    runYear(sys.argv[1])
