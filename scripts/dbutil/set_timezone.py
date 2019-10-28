"""
Set time zones of stations using the shapefile found here:

http://efele.net/maps/tz/world/
"""
from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    mcursor2 = pgconn.cursor()

    mcursor.execute(
        """
         SELECT id, network, ST_x(geom) as lon, ST_y(geom) as lat from stations
         WHERE tzname is null
     """
    )

    for row in mcursor:
        lat = row[3]
        lon = row[2]
        sid = row[0]
        network = row[1]

        mcursor2.execute(
            """
        select tzid from tz_world where ST_Intersects(geom,
        ST_GeomFromText('SRID=4326;POINT(%s %s)'));
          """
            % (lon, lat)
        )
        row2 = mcursor2.fetchone()
        if row2 is None or row2[0] == "uninhabited":
            LOG.info(
                "MISSING TZ ID: %s NETWORK: %s LAT: %.2f LON: %.2f",
                sid,
                network,
                lat,
                lon,
            )
            mcursor2.execute(
                """
                SELECT ST_Distance(geom, 'SRID=4326;POINT(%s %s)') as d,
                id, tzname from stations WHERE network = %s
                and tzname is not null ORDER by d ASC LIMIT 1
            """,
                (lon, lat, network),
            )
            row3 = mcursor2.fetchone()
            if row3 is not None:
                LOG.info(
                    "FORCING tz to its neighbor: %s Tzname: %s Dist: %.5f",
                    row3[1],
                    row3[2],
                    row3[0],
                )
                mcursor2.execute(
                    """
                    UPDATE stations SET tzname = %s
                    WHERE id = %s and network = %s
                """,
                    (row3[2], sid, network),
                )
            else:
                mcursor2.execute(
                    """
                    SELECT tzname from networks where id = %s
                """,
                    (network,),
                )
                if mcursor2.rowcount == 1:
                    tzname = mcursor2.fetchone()[0]
                    LOG.info("%s using network default of %s", sid, tzname)
                    mcursor2.execute(
                        """
                        UPDATE stations SET tzname = %s
                        WHERE id = %s and network = %s
                    """,
                        (tzname, sid, network),
                    )
        else:
            LOG.info("ID: %s NETWORK: %s TIMEZONE: %s", sid, network, row2[0])
            mcursor2.execute(
                """
                UPDATE stations SET tzname = %s
                WHERE id = %s and network = %s
            """,
                (row2[0], sid, network),
            )

    mcursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
