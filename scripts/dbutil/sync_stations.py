"""
 My purpose in life is to sync the mesosite stations table to other
databases.  This will hopefully remove some hackery
"""
import datetime
import sys

from pyiem.util import get_dbconn, logger
import psycopg2.extras

LOG = logger()


def sync(mesosite, dbname, do_delete):
    """
    Actually do the syncing, please
    """
    # connect to synced database
    dbconn = get_dbconn(dbname)
    dbcursor = dbconn.cursor()
    # Figure out our latest revision
    dbcursor.execute(
        """
        SELECT max(modified), max(iemid) from stations
    """
    )
    row = dbcursor.fetchone()
    maxts = row[0] or datetime.datetime(1980, 1, 1)
    maxid = row[1] or -1
    cur = mesosite.cursor(cursor_factory=psycopg2.extras.DictCursor)
    todelete = []
    if do_delete:
        # Generate massive listing of all NWSLIs
        cur.execute("""SELECT iemid from stations""")
        iemids = []
        for row in cur:
            iemids.append(row[0])
        # Find what iemids we have in local database
        dbcursor.execute("""SELECT iemid from stations""")
        for row in dbcursor:
            if row[0] not in iemids:
                todelete.append(row[0])
        if todelete:
            dbcursor.execute(
                """
                DELETE from stations where iemid in %s
            """,
                (tuple(todelete),),
            )
    # figure out what has changed!
    cur.execute(
        """
        SELECT * from stations WHERE modified > %s or iemid > %s
    """,
        (maxts, maxid),
    )
    for row in cur:
        if row["iemid"] > maxid:
            dbcursor.execute(
                """
                INSERT into stations(iemid, network, id)
                VALUES(%s,%s,%s)
            """,
                (row["iemid"], row["network"], row["id"]),
            )
        # insert queried stations
        dbcursor.execute(
            """
            UPDATE stations SET name = %(name)s,
            state = %(state)s, elevation = %(elevation)s, online = %(online)s,
            geom = %(geom)s, params = %(params)s, county = %(county)s,
            plot_name = %(plot_name)s, climate_site = %(climate_site)s,
            wfo = %(wfo)s, archive_begin = %(archive_begin)s,
            archive_end = %(archive_end)s, remote_id = %(remote_id)s,
            tzname = %(tzname)s, country = %(country)s,
            modified = %(modified)s, network = %(network)s,
            metasite = %(metasite)s,
            sigstage_low = %(sigstage_low)s,
            sigstage_action = %(sigstage_action)s,
            sigstage_bankfull = %(sigstage_bankfull)s,
            sigstage_flood = %(sigstage_flood)s,
            sigstage_moderate = %(sigstage_moderate)s,
            sigstage_major = %(sigstage_major)s,
            sigstage_record = %(sigstage_record)s, ugc_county = %(ugc_county)s,
            ugc_zone = %(ugc_zone)s, id = %(id)s, ncdc81 = %(ncdc81)s,
            temp24_hour = %(temp24_hour)s, precip24_hour = %(precip24_hour)s
            WHERE iemid = %(iemid)s
       """,
            row,
        )
    LOG.info(
        "DB: %-7s Del %3s Mod %4s rows TS: %s IEMID: %s",
        dbname,
        len(todelete),
        cur.rowcount,
        maxts.strftime("%Y/%m/%d %H:%M"),
        maxid,
    )
    # close connection
    dbcursor.close()
    dbconn.commit()
    dbconn.close()


def main(argv):
    """Go Main Go"""
    mesosite = get_dbconn("mesosite")
    subscribers = ["iem", "coop", "hads", "asos", "postgis"]

    do_delete = False
    if len(argv) == 2:
        LOG.info("Running with delete option set, this will be slow")
        do_delete = True

    if len(argv) == 3:
        LOG.info(
            (
                "Running laptop syncing from upstream, "
                "assume iemdb is localhost!"
            )
        )
        # HACK
        mesosite = get_dbconn("mesosite", host="172.16.172.1", user="nobody")
        subscribers.insert(0, "mesosite")
    for sub in subscribers:
        sync(mesosite, sub, do_delete)


if __name__ == "__main__":
    main(sys.argv)
