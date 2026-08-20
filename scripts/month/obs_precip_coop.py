"""Generate a map of this month's observed precip"""

from datetime import date, timedelta

from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import MapPlot


def main():
    """Go Main Go"""
    now = date.today()

    day1 = now.replace(day=1)
    day2 = (now + timedelta(days=35)).replace(day=1)

    lats = []
    lons = []
    precip = []
    labels = []
    with get_sqlalchemy_conn("iem") as conn:
        res = conn.execute(
            sql_helper(
                """SELECT id,
        sum(pday) as precip,
        sum(CASE when pday is null THEN 1 ELSE 0 END) as missing,
        ST_x(s.geom) as lon, ST_y(s.geom) as lat
        from {table} c JOIN stations s
        ON (s.iemid = c.iemid)
        WHERE s.network in ('IA_COOP') and s.iemid = c.iemid and
        day >= :day1 and day < :day2
        GROUP by id, lat, lon""",
                table=f"summary_{now:%Y}",
            ),
            {"day1": day1, "day2": day2},
        )
        for row in res.mappings():
            if row["missing"] > (now.day / 3) or row["precip"] is None:
                continue

            sid = row["id"]
            labels.append(sid)
            lats.append(row["lat"])
            lons.append(row["lon"])
            precip.append(row["precip"])

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
