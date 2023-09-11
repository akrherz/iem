"""Generate a map of this month's observed precip"""
import datetime

from pyiem.plot import MapPlot
from pyiem.util import get_dbconnc


def main():
    """Go Main Go"""
    now = datetime.date.today()
    pgconn, icursor = get_dbconnc("iem")

    day1 = now.replace(day=1)
    day2 = (now + datetime.timedelta(days=35)).replace(day=1)

    # Compute normal from the climate database
    sql = """SELECT id,
        sum(pday) as precip,
        sum(CASE when pday is null THEN 1 ELSE 0 END) as missing,
        ST_x(s.geom) as lon, ST_y(s.geom) as lat
        from summary_%s c JOIN stations s
        ON (s.iemid = c.iemid)
        WHERE s.network in ('IA_COOP') and s.iemid = c.iemid and
        day >= '%s' and day < '%s'
        GROUP by id, lat, lon""" % (
        now.year,
        day1.strftime("%Y-%m-%d"),
        day2.strftime("%Y-%m-%d"),
    )

    lats = []
    lons = []
    precip = []
    labels = []
    icursor.execute(sql)
    for row in icursor:
        if row["missing"] > (now.day / 3) or row[1] is None:
            continue

        sid = row["id"]
        labels.append(sid)
        lats.append(row["lat"])
        lons.append(row["lon"])
        precip.append(row["precip"])
    pgconn.close()

    mp = MapPlot(
        title="This Month's Precipitation [inch] (NWS COOP Network)",
        subtitle=now.strftime("%b %Y"),
        axisbg="white",
    )
    mp.plot_values(lons, lats, precip, fmt="%.2f", labels=labels)
    mp.drawcounties()
    pqstr = "plot c 000000000000 coopMonthPlot.png bogus png"
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
