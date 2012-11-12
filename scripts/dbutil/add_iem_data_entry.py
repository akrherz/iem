"""
 Main script that adds a site into the appropriate tables
"""

import sys
import mx.DateTime
import iemdb
import psycopg2.extras

IEM = iemdb.connect('iem')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Find sites that are online and not metasites that are not in the current
# table!
icursor.execute("""
 SELECT iemid, id, network from stations where 
     iemid not in (select iemid from current)
     and online and metasite = 'f' ORDER by iemid ASC
""")

for row in icursor:
    print "Adding station ID: %s NETWORK: %s" % (row['id'], row['network'])

    for tbl in ['trend_1h', 'trend_15m']:
        icursor.execute("""INSERT into %s (iemid)
          VALUES ( %s) """ % (tbl,  row['iemid'] ) )
  
    tbl = 'summary_%s' % (mx.DateTime.now().year,)
    icursor.execute("""INSERT into %s ( day, iemid)
          VALUES ('TODAY', %s) """ % (tbl, 
          row['iemid'] ) )
    tbl = 'summary_%s' % ((mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=1)).year,)
    icursor.execute("""INSERT into %s ( day, iemid)
          VALUES ( 'TOMORROW', %s) """ % (tbl,
          row['iemid'] ) )
    tbl = 'current'
    icursor.execute("""INSERT into %s ( valid, iemid)
          VALUES ('1980-01-01', %s) """ % (tbl,
          row['iemid'] ) )

icursor.close()
IEM.commit()
IEM.close()


