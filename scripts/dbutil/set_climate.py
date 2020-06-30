"""
 Assign a climate site to each site in the mesosite database, within reason
"""

from pyiem.util import get_dbconn


def workflow(col):
    """Query out all sites with a null climate_site"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    mcursor2 = pgconn.cursor()
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
        # Don't attempt to assign a climate_site to sites outside of mainland
        if col == "climate_site" and st in [
            "PR",
            "DC",
            "GU",
            "PU",
            "P1",
            "P2",
            "P3",
            "P4",
            "P5",
            "VI",
            "HI",
            "AK",
        ]:
            continue
        # Find the closest site
        if col == "climate_site":
            sql = """
                select id from stations WHERE network = '%sCLIMATE'
                and substr(id,3,4) != '0000' and substr(id,3,1) != 'C'
                ORDER by ST_distance(geom, '%s') ASC LIMIT 1
            """ % (
                st,
                geom,
            )
        else:
            sql = """
                select id from stations WHERE network = 'NCDC81'
                ORDER by ST_distance(geom, '%s') ASC LIMIT 1
            """ % (
                geom,
            )
        mcursor2.execute(sql)
        row2 = mcursor2.fetchone()
        if row2 is None:
            print("Could not find %s site for: %s" % (col, sid))
        else:
            sql = """
                UPDATE stations SET %s = '%s' WHERE iemid = %s
            """ % (
                col,
                row2[0],
                iemid,
            )
            mcursor2.execute(sql)
            print("Set %s: %s for ID: %s[%s]" % (col, row2[0], sid, network))
    mcursor2.close()
    pgconn.commit()


def main():
    """Go Main Go"""
    workflow("climate_site")
    workflow("ncdc81")


if __name__ == "__main__":
    main()
