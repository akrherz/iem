"""Generate a map of this month's observed precip"""

import datetime

import pyiem.tracker
from pyiem.plot import MapPlot
from pyiem.util import get_dbconnc


def main():
    """Go Main Go"""
    now = datetime.datetime.now()

    qdict = pyiem.tracker.loadqc()

    pgconn, icursor = get_dbconnc("iem")

    # Compute normal from the climate database
    sql = """SELECT id,
          sum(pday) as precip,
          ST_x(geom) as lon, ST_y(geom) as lat from summary_%s s, stations t
         WHERE t.network = 'IA_ASOS' and
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
        sid = row["id"]
        labels.append(sid)
        lats.append(row["lat"])
        lons.append(row["lon"])
        if (
            not qdict.get(sid, {}).get("precip", False)
            and row["precip"] is not None
        ):
            precip.append("%.2f" % (row["precip"],))
        else:
            precip.append("M")
    pgconn.close()
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
