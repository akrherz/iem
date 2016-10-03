"""
 My purpose in life is to sync the mesosite stations table to other
databases.  This will hopefully remove some hackery
"""

import datetime
import sys
import psycopg2.extras
MESOSITE = psycopg2.connect(database="mesosite", host='iemdb')
subscribers = ["iem", "coop", "hads", "asos", "postgis"]

DO_DELETE = False
if len(sys.argv) == 2:
    print 'Running with delete option set, this will be slow'
    DO_DELETE = True

if len(sys.argv) == 3:
    print 'Running laptop syncing from upstream, assume iemdb is localhost!'
    MESOSITE = psycopg2.connect(database='mesosite',
                                host='129.186.185.33',
                                user='nobody')
    subscribers.insert(0, 'mesosite')


def sync(dbname):
    """
    Actually do the syncing, please
    """
    # connect to synced database
    dbhost = "iemdb" if dbname != 'hads' else 'iemdb-hads'
    dbconn = psycopg2.connect(database=dbname, host=dbhost)
    dbcursor = dbconn.cursor()
    # Figure out our latest revision
    dbcursor.execute("""
    SELECT max(modified), max(iemid) from stations
    """)
    row = dbcursor.fetchone()
    maxTS = (row[0] or datetime.datetime(1980, 1, 1))
    maxID = (row[1] or -1)
    cur = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)
    todelete = []
    if DO_DELETE:
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
        if len(todelete) > 0:
            dbcursor.execute("""DELETE from stations where iemid in %s
            """, (tuple(todelete), ))
    # figure out what has changed!
    cur.execute("""SELECT * from stations WHERE modified > %s or iemid > %s""",
                (maxTS, maxID))
    for row in cur:
        if row['iemid'] > maxID:
            dbcursor.execute("""INSERT into stations(iemid, network, id)
             VALUES(%s,%s,%s) """, (row['iemid'], row['network'], row['id']))
        # insert queried stations
        dbcursor.execute("""UPDATE stations SET name = %(name)s,
       state = %(state)s, elevation = %(elevation)s, online = %(online)s,
       geom = %(geom)s, params = %(params)s, county = %(county)s,
       plot_name = %(plot_name)s, climate_site = %(climate_site)s,
       wfo = %(wfo)s, archive_begin = %(archive_begin)s,
       archive_end = %(archive_end)s, remote_id = %(remote_id)s,
       tzname = %(tzname)s, country = %(country)s,
       modified = %(modified)s, network = %(network)s, metasite = %(metasite)s,
       sigstage_low = %(sigstage_low)s, sigstage_action = %(sigstage_action)s,
       sigstage_bankfull = %(sigstage_bankfull)s,
       sigstage_flood = %(sigstage_flood)s,
       sigstage_moderate = %(sigstage_moderate)s,
       sigstage_major = %(sigstage_major)s,
       sigstage_record = %(sigstage_record)s, ugc_county = %(ugc_county)s,
       ugc_zone = %(ugc_zone)s, id = %(id)s, ncdc81 = %(ncdc81)s,
       temp24_hour = %(temp24_hour)s, precip24_hour = %(precip24_hour)s
       WHERE iemid = %(iemid)s""", row)
    print ("DB: %-7s Del %3s Mod %4s rows TS: %s IEMID: %s"
           "") % (dbname, len(todelete), cur.rowcount,
                  maxTS.strftime("%Y/%m/%d %H:%M"), maxID)
    # close connection
    dbcursor.close()
    dbconn.commit()
    dbconn.close()


def main():
    for sub in subscribers:
        sync(sub)
    MESOSITE.close()

if __name__ == '__main__':
    main()
