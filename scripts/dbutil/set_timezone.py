"""
Set time zones of stations using the shapefile found here:

http://efele.net/maps/tz/world/
"""

from pyiem.util import get_dbconnc, logger

LOG = logger()


def main():
    """Go Main"""
    pgconn, mcursor = get_dbconnc("mesosite")
    mcursor2 = pgconn.cursor()

    mcursor.execute(
        "SELECT id, network, ST_x(geom) as lon, ST_y(geom) as lat "
        "from stations WHERE tzname is null"
    )

    for row in mcursor:
        lat = row["lat"]
        lon = row["lon"]
        sid = row["id"]
        network = row["network"]

        mcursor2.execute(
            """
        select tzid from tz_world where ST_Intersects(geom,
        ST_Point(%s, %s, 4326));
          """,
            (lon, lat),
        )
        row2 = mcursor2.fetchone()
        if row2 is None or row2["tzid"] == "uninhabited":
            LOG.info(
                "MISSING TZ ID: %s NETWORK: %s LAT: %.2f LON: %.2f",
                sid,
                network,
                lat,
                lon,
            )
            mcursor2.execute(
                """
                SELECT ST_Distance(geom, ST_Point(%s, %s, 4326)) as d,
                id, tzname from stations WHERE network = %s
                and tzname is not null ORDER by d ASC LIMIT 1
            """,
                (lon, lat, network),
            )
            row3 = mcursor2.fetchone()
            if row3 is not None:
                LOG.info(
                    "FORCING tz to its neighbor: %s Tzname: %s Dist: %.5f",
                    row3["id"],
                    row3["tzname"],
                    row3["d"],
                )
                mcursor2.execute(
                    """
                    UPDATE stations SET tzname = %s
                    WHERE id = %s and network = %s
                """,
                    (row3["tzname"], sid, network),
                )
            else:
                mcursor2.execute(
                    "SELECT tzname from networks where id = %s", (network,)
                )
                if mcursor2.rowcount == 1:
                    tzname = mcursor2.fetchone()["tzname"]
                    LOG.info("%s using network default of %s", sid, tzname)
                    mcursor2.execute(
                        """
                        UPDATE stations SET tzname = %s
                        WHERE id = %s and network = %s
                    """,
                        (tzname, sid, network),
                    )
        else:
            LOG.info(
                "ID: %s NETWORK: %s TIMEZONE: %s", sid, network, row2["tzid"]
            )
            mcursor2.execute(
                "UPDATE stations SET tzname = %s "
                "WHERE id = %s and network = %s",
                (row2["tzid"], sid, network),
            )

    mcursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
