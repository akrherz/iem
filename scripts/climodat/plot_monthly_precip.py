"""
 Create a contour plot of monthly precip from the climodat data (iemre)
"""
import sys
import psycopg2.extras
from pyiem.plot import MapPlot
import mx.DateTime
from pyiem.network import Table as NetworkTable

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
nt = NetworkTable("IACLIMATE")


def do_month(ts, routes='m'):
    """
    Generate the plot for a given month, please
    """
    sql = """SELECT station, sum(precip) as total, max(day) as lastday
           from alldata_ia WHERE year = %s and month = %s
           and station != 'IA0000' and substr(station,2,1) != 'C'
           GROUP by station""" % (ts.year, ts.month)

    lats = []
    lons = []
    vals = []
    lastday = None
    ccursor.execute(sql)
    for row in ccursor:
        if row['station'] not in nt.sts:
            continue
        if lastday is None:
            lastday = row['lastday']
        lats.append(nt.sts[row['station']]['lat'])
        lons.append(nt.sts[row['station']]['lon'])
        vals.append(row['total'])

    m = MapPlot(title='%s - %s' % (ts.strftime("%d %B %Y"),
                                   lastday.strftime("%d %B %Y")),
                subtitle="%s Total Precipitation [inch]" % (
                                    ts.strftime("%B %Y"),))
    m.contourf(lons, lats, vals, [0, 0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5, 6,
                                  7])
    m.plot_values(lons, lats, vals, fmt='%.2f')

    pqstr = ("plot %s %s summary/iemre_iowa_total_precip.png "
             "%s/summary/iemre_iowa_total_precip.png png"
             ) % (routes, ts.strftime("%Y%m%d%H%M"), ts.strftime("%Y/%m"))
    m.postprocess(pqstr=pqstr)


def main():
    """Do Something"""
    if len(sys.argv) == 3:
        now = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]))
        do_month(now, 'm')
    else:
        now = (mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1) +
               mx.DateTime.RelativeDateTime(day=1))
        do_month(now, 'cm')


if __name__ == '__main__':
    main()
