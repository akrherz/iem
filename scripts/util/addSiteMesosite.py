"""
 Main script that adds a site into the appropriate tables
 $Id: $:
"""

import sys, mx.DateTime
import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
IEM = iemdb.connect('iem')
icursor = IEM.cursor()

_NETWORK = sys.argv[1]
_ID = sys.argv[2]

mcursor.execute("""SELECT * from stations WHERE network = '%s' 
   and id = '%s' LIMIT 1""" % (_NETWORK, _ID) )

for row in mcursor:
    print "Adding station :%s:" % (_ID,)

    for tbl in ['trend_1h', 'trend_15m']:
        icursor.execute("""INSERT into %s (station, network)
          VALUES ('%s', '%s') """ % (tbl, _ID, _NETWORK ) )
  
    tbl = 'summary_%s' % (mx.DateTime.now().year,)
    icursor.execute("""INSERT into %s (station, network, day)
          VALUES ('%s', '%s', 'TODAY') """ % (tbl, _ID, _NETWORK ) )
    icursor.execute("""INSERT into %s (station, network, day)
          VALUES ('%s', '%s', 'TOMORROW') """ % (tbl, _ID, _NETWORK ) )
    tbl = 'current'
    icursor.execute("""INSERT into %s (station, network, valid)
          VALUES ('%s', '%s', '1980-01-01') """ % (tbl, _ID, _NETWORK ) )

icursor.close()
IEM.commit()
IEM.close()


