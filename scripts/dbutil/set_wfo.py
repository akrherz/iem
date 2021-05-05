"""Assign a WFO to sites in the metadata tables that have no WFO set."""

from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main"""
    mesosite = get_dbconn("mesosite")
    postgis = get_dbconn("postgis")
    mcursor = mesosite.cursor()
    mcursor2 = mesosite.cursor()
    pcursor = postgis.cursor()

    # Find sites we need to check on
    mcursor.execute(
        "select s.id, s.iemid, s.network, st_x(geom) as lon, "
        "st_y(geom) as lat from stations s WHERE "
        "(s.wfo IS NULL or s.wfo = '') and s.country = 'US'"
    )

    for row in mcursor:
        sid = row[0]
        iemid = row[1]
        network = row[2]
        # Look for WFO that
        pcursor.execute(
            "select wfo from cwa WHERE "
            "ST_Contains(the_geom, "
            "  ST_SetSrid(ST_GeomFromEWKT('POINT(%s %s)'), 4326)) ",
            (row[3], row[4]),
        )
        if pcursor.rowcount == 0:
            LOG.info(
                "IEMID: %s ID: %s NETWORK: %s not within CWAs, calc dist",
                iemid,
                sid,
                network,
            )
            pcursor.execute(
                "SELECT wfo, ST_Distance(the_geom, "
                "  ST_SetSrid(ST_GeomFromEWKT('POINT(%s %s)'), 4326)) as dist "
                "from cwa ORDER by dist ASC LIMIT 1",
                (row[3], row[4]),
            )
            wfo, dist = pcursor.fetchone()
            if dist > 3:
                LOG.info(
                    "    closest CWA %s found >3 degrees away %.2f",
                    wfo,
                    dist,
                )
                continue
        else:
            row2 = pcursor.fetchone()
            wfo = row2[0][:3]
        LOG.info(
            "Assinging WFO: %s to IEMID: %s ID: %s NETWORK: %s",
            wfo,
            iemid,
            sid,
            network,
        )
        mcursor2.execute(
            "UPDATE stations SET wfo = %s WHERE iemid = %s", (wfo, iemid)
        )

    mcursor.close()
    mcursor2.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
