"""Assign a WFO to sites in the metadata tables that have no WFO set."""
from __future__ import print_function

from pyiem.util import get_dbconn, logger


def main():
    """Go Main"""
    log = logger()
    mesosite = get_dbconn("mesosite")
    postgis = get_dbconn("postgis")
    mcursor = mesosite.cursor()
    mcursor2 = mesosite.cursor()
    pcursor = postgis.cursor()

    # Find sites we need to check on
    mcursor.execute(
        """
        select s.id, s.iemid, s.network, st_x(geom) as lon, st_y(geom) as lat
        from stations s WHERE
        (s.wfo IS NULL or s.wfo = '') and s.country = 'US'
    """
    )

    for row in mcursor:
        sid = row[0]
        iemid = row[1]
        network = row[2]
        # Look for matching WFO
        pcursor.execute(
            """
            WITH s as (
                SELECT
                ST_SetSrid(ST_GeomFromEWKT('POINT(%s %s)'), 4326) as geom
            )
            select u.wfo, ST_Distance(u.geom, s.geom) as dist
            from s, ugcs u WHERE ST_Intersects(u.geom, s.geom) and
            u.end_ts is null and wfo is not null ORDER by dist ASC LIMIT 1
        """,
            (row[3], row[4]),
        )
        if pcursor.rowcount > 0:
            row2 = pcursor.fetchone()
            wfo = row2[0][:3]
            log.info(
                "Assinging WFO: %s to IEMID: %s ID: %s NETWORK: %s",
                wfo,
                iemid,
                sid,
                network,
            )
            mcursor2.execute(
                """
                UPDATE stations SET wfo = '%s' WHERE iemid = %s
            """
                % (wfo, iemid)
            )
        else:
            log.info(
                "ERROR assigning WFO to IEMID: %s ID: %s NETWORK: %s",
                iemid,
                sid,
                network,
            )

    mcursor.close()
    mcursor2.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
