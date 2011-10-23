# My purpose in life is to sync the mesosite stations table to other
# databases.  This will hopefully remove some hackery

import iemdb
import datetime
import psycopg2
import psycopg2.extras
MESOSITE = iemdb.connect("mesosite")
subscribers = ["iem","coop","hads"]

def sync(dbname):
    """
    Actually do the syncing, please
    """
    # connect to synced database
    dbconn = iemdb.connect( dbname )
    dbcursor = dbconn.cursor()
    # Figure out our latest revision
    dbcursor.execute("""
    SELECT max(modified), max(iemid) from stations
    """)
    row = dbcursor.fetchone()
    maxTS = (row[0] or datetime.datetime(1980,1,1))
    maxID = (row[1] or -1)
    # figure out what has changed!
    cur = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""SELECT * from stations WHERE modified > %s or iemid > %s""",
    (maxTS, maxID) )
    for row in cur:
      if row['iemid'] > maxID:
        dbcursor.execute("""INSERT into stations(iemid, network, id) 
         VALUES('%s','%s','%s') """, (row['iemid'], row['network'], row['id']))
      # insert queried stations
      dbcursor.execute("""UPDATE stations SET name = %(name)s, 
       state = %(state)s, elevation = %(elevation)s, online = %(online)s, 
       geom = %(geom)s, params = %(params)s, county = %(county)s, 
       plot_name = %(plot_name)s, climate_site = %(climate_site)s,
       wfo = %(wfo)s, archive_begin = %(archive_begin)s, 
       archive_end = %(archive_end)s, remote_id = %(remote_id)s, 
       tzname = %(tzname)s, country = %(country)s, 
       modified = %(modified)s
       WHERE iemid = %(iemid)s""",
       row)
    print 'Database: %s Modified %s rows TS: %s IEMID: %s' % (dbname, 
       cur.rowcount, maxTS, maxID)
    # close connection
    dbcursor.close()
    dbconn.commit()
    dbconn.close()

for sub in subscribers:
    sync(sub)
MESOSITE.close()
