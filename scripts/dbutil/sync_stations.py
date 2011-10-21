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
      # delete current stations in dest
      dbcursor.execute("""DELETE from stations WHERE iemid = %s or 
       (network = %s and id = %s)""", (row['iemid'], row['network'], row['id']))
      # insert queried stations
      dbcursor.execute("""INSERT into stations(id, name, state,
     elevation, network, online, geom, params, county, plot_name, climate_site,
     wfo, archive_begin, archive_end, remote_id, tzname, country, iemid,
     modified) 
     values (%(id)s,
      %(name)s, %(state)s, %(elevation)s, %(network)s, %(online)s,
     %(geom)s, %(params)s, %(county)s, %(plot_name)s, %(climate_site)s,
     %(wfo)s, %(archive_begin)s, %(archive_end)s, %(remote_id)s,
     %(tzname)s, %(country)s, %(iemid)s, %(modified)s)""",
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
