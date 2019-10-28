""" Generate a map of this month's observed precip"""

import datetime

from pyiem.plot import MapPlot
import pyiem.tracker
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    now = datetime.datetime.now()

    qdict = pyiem.tracker.loadqc()

    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    # Compute normal from the climate database
    sql = """SELECT id,
          sum(pday) as precip,
          ST_x(geom) as lon, ST_y(geom) as lat from summary_%s s, stations t
         WHERE t.network in ('IA_ASOS', 'AWOS') and
          extract(month from day) = %s
          and extract(year from day) = extract(year from now())
         and t.iemid = s.iemid GROUP by id, lat, lon
    """ % (
        now.year,
        now.strftime("%m"),
    )

    lats = []
    lons = []
    precip = []
    labels = []
    icursor.execute(sql)
    for row in icursor:
        sid = row[0]
        labels.append(sid)
        lats.append(row[3])
        lons.append(row[2])
        if not qdict.get(sid, {}).get("precip", False) and row[1] is not None:
            precip.append("%.2f" % (row[1],))
        else:
            precip.append("M")

    mp = MapPlot(
        title="This Month's Precipitation [inch]",
        subtitle=now.strftime("%b %Y"),
        axisbg="white",
    )
    mp.plot_values(lons, lats, precip, labels=labels)
    pqstr = "plot c 000000000000 summary/month_prec.png bogus png"
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
