"""Generate a map of Yearly Precipitation
"""

import sys
from pyiem.plot import MapPlot
import datetime
import psycopg2.extras
from pyiem.network import Table as NetworkTable
now = datetime.datetime.now()
nt = NetworkTable("IACLIMATE")
# Help plot readability
nt.sts["IA0200"]["lon"] = -93.4
nt.sts["IA5992"]["lat"] = 41.65
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)


def runYear(year):
    # Grab the data
    sql = """SELECT station, sum(precip) as total, max(day)
           from alldata_ia WHERE year = %s and
           station != 'IA0000' and
           substr(station,3,1) != 'C' and
           precip is not null GROUP by station""" % (year,)

    lats = []
    lons = []
    vals = []
    labels = []
    ccursor.execute(sql)
    for row in ccursor:
        sid = row['station']
        if sid not in nt.sts:
            continue
        labels.append(sid[2:])
        lats.append(nt.sts[sid]['lat'])
        lons.append(nt.sts[sid]['lon'])
        vals.append(row['total'])
        maxday = row['max']

    m = MapPlot(title="Total Precipitation [inch] (%s)" % (year,),
                subtitle='1 January - %s' % (maxday.strftime("%d %B"),),
                axisbg='white')
    m.plot_values(lons, lats, vals, labels=labels, fmt='%.2f',
                  labeltextsize=8, labelcolor='tan')
    pqstr = "plot m %s bogus %s/summary/total_precip.png png" % (
                                        now.strftime("%Y%m%d%H%M"), year,)
    m.postprocess(pqstr=pqstr)


if __name__ == '__main__':
    runYear(sys.argv[1])
