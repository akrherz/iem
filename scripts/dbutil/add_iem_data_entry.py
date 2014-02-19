"""
 Main script that adds a site into the appropriate tables
 called from SYNC_STATIONS.sh
"""

import datetime
import psycopg2
import psycopg2.extras

IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
icursor2 = IEM.cursor()

# Find sites that are online and not metasites that are not in the current
# table!
icursor.execute("""
 SELECT iemid, id, network from stations where 
     iemid not in (select iemid from current)
     and online and metasite = 'f' ORDER by iemid ASC
""")

utcnow = datetime.datetime.utcnow()

for row in icursor:
    print "Adding station ID: %10s NETWORK: %s" % (row['id'], row['network'])

    for tbl in ['trend_1h', 'trend_15m']:
        icursor2.execute("""INSERT into %s (iemid)
          VALUES ( %s) """ % (tbl,  row['iemid'] ) )
  
    tbl = 'summary_%s' % (utcnow.year,)
    icursor2.execute("""INSERT into %s ( day, iemid)
          VALUES ('TODAY', %s) """ % (tbl, 
          row['iemid'] ) )
    
    tbl = 'summary_%s' % ((utcnow + datetime.timedelta(days=1)).year,)
    icursor2.execute("""INSERT into %s ( day, iemid)
          VALUES ( 'TOMORROW', %s) """ % (tbl,
          row['iemid'] ) )
    tbl = 'current'
    icursor2.execute("""INSERT into %s ( valid, iemid)
          VALUES ('1980-01-01', %s) """ % (tbl,
          row['iemid'] ) )

icursor2.close()
IEM.commit()
IEM.close()


