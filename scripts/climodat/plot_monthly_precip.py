"""
 Create a contour plot of monthly precip from the climodat data (iemre)
"""
import sys
import datetime

import psycopg2.extras
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def do_month(ts, routes="m"):
    """
    Generate the plot for a given month, please
    """
    pgconn = get_dbconn("coop", user="nobody")
    ccursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    nt = NetworkTable("IACLIMATE")
    sql = """SELECT station, sum(precip) as total, max(day) as lastday
           from alldata_ia WHERE year = %s and month = %s
           and station != 'IA0000' and substr(station,2,1) != 'C'
           GROUP by station""" % (
        ts.year,
        ts.month,
    )

    lats = []
    lons = []
    vals = []
    lastday = None
    ccursor.execute(sql)
    for row in ccursor:
        if row["station"] not in nt.sts:
            continue
        if lastday is None:
            lastday = row["lastday"]
        lats.append(nt.sts[row["station"]]["lat"])
        lons.append(nt.sts[row["station"]]["lon"])
        vals.append(row["total"])

    mp = MapPlot(
        title="%s - %s"
        % (ts.strftime("%d %B %Y"), lastday.strftime("%d %B %Y")),
        subtitle="%s Total Precipitation [inch]" % (ts.strftime("%B %Y"),),
    )
    mp.contourf(
        lons, lats, vals, [0, 0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5, 6, 7]
    )
    mp.plot_values(lons, lats, vals, fmt="%.2f")

    pqstr = (
        "plot %s %s summary/iemre_iowa_total_precip.png "
        "%s/summary/iemre_iowa_total_precip.png png"
    ) % (routes, ts.strftime("%Y%m%d%H%M"), ts.strftime("%Y/%m"))
    mp.postprocess(pqstr=pqstr)


def main(argv):
    """Do Something"""
    if len(argv) == 3:
        now = datetime.datetime(int(argv[1]), int(argv[2]), 1)
        do_month(now, "m")
    else:
        now = datetime.datetime.now() - datetime.timedelta(days=1)
        now = now.replace(day=1)
        do_month(now, "cm")


if __name__ == "__main__":
    main(sys.argv)
