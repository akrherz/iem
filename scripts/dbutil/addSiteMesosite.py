"""
 Main script that adds a site into the appropriate tables
 $Id: $:
"""

import sys, mx.DateTime
import iemdb
import psycopg2.extras
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)
IEM = iemdb.connect('iem')
icursor = IEM.cursor()

# Figure out the highest ID we have from current table
icursor.execute("""SELECT max(iemid) from current""")
row = icursor.fetchone()
maxID = row[0]

# Figure out new stations
if len(sys.argv) == 3:
    mcursor.execute("""SELECT * from stations WHERE id = %s and network = %s""" , (sys.argv[2],sys.argv[1]) )
else:
    mcursor.execute("""SELECT * from stations WHERE online and iemid > %s""" % (maxID,) )

for row in mcursor:
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


