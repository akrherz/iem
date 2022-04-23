"""
 Assign a climate site to each site in the mesosite database, within reason
"""

from pyiem.util import get_dbconn, logger

LOG = logger()


def workflow(col):
    """Query out all sites with a null climate_site"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    mcursor2 = pgconn.cursor()
    if col == "climate_site":
        # Update when sites come offline and online
        mcursor.execute(
            "update stations SET climate_site = null where "
            "climate_site not in (select id from stations where "
            "network ~* 'CLIMATE' and online)"
        )
        if mcursor.rowcount > 0:
            LOG.info(
                "Found %s entries with now offline climate stations",
                mcursor.rowcount,
            )
    mcursor.execute(
        f"SELECT id, geom, state, iemid, network from stations WHERE {col} "
        "IS NULL and country = 'US' and state is not null"
    )
    for row in mcursor:
        sid = row[0]
        geom = row[1]
        st = row[2]
        iemid = row[3]
        network = row[4]
        # Don't attempt to assign a climate_site for places we have no data
        if col == "climate_site" and st in [
            "PU",
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
        ]:
            continue
        # Find the closest site
        if col == "climate_site":
            sql = (
                f"select id from stations WHERE network = '{st}CLIMATE' "
                "and substr(id,3,4) != '0000' and substr(id,3,1) != 'C' "
                "and online ORDER by ST_distance(geom, %s) ASC LIMIT 1"
            )
        else:
            clnetwork = "NCDC81" if col == "ncdc81" else "NCEI91"
            sql = (
                f"select id from stations WHERE network = '{clnetwork}' "
                "ORDER by ST_distance(geom, %s) ASC LIMIT 1"
            )
        mcursor2.execute(sql, (geom,))
        row2 = mcursor2.fetchone()
        if row2 is None:
            LOG.info("Could not find %s site for: %s", col, sid)
        else:
            mcursor2.execute(
                f"UPDATE stations SET {col} = %s WHERE iemid = %s",
                (row2[0], iemid),
            )
            LOG.info("Set %s: %s for ID: %s[%s]", col, row2[0], sid, network)
    mcursor2.close()
    pgconn.commit()


def main():
    """Go Main Go"""
    workflow("climate_site")
    workflow("ncdc81")
    workflow("ncei91")


if __name__ == "__main__":
    main()
