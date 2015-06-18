'''
  Remove a station from realtime data collection and tracking
'''
import psycopg2
import sys
import datetime
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()
year = datetime.datetime.now().year

if len(sys.argv) != 3:
    print 'Usage: python remove_realtime.py NETWORK SID'
    sys.exit()

for table in ['current', ]:
    icursor.execute("""
     DELETE from %s where 
     iemid = (select iemid from stations where id = '%s' and network = '%s')
    """ % (table, sys.argv[2], sys.argv[1]))
    if icursor.rowcount != 1:
        print 'Updating table: %s resulted in %s rows modified' % (table,
                                                        icursor.rowcount)

icursor.execute("""
 DELETE from %s where 
 iemid = (select iemid from stations where id = '%s' and network = '%s')
 and day in ('TODAY','TOMORROW')
""" % ('summary_%s' % (year,), sys.argv[2], sys.argv[1]))
if icursor.rowcount != 2:
    print 'Updating table: %s resulted in %s rows modified' % ('summary',
                                                    icursor.rowcount)


icursor.close()
IEM.commit()

mcursor.execute("""
update stations SET online = false where id = '%s' and network = '%s'
""" % (sys.argv[2],sys.argv[1]))
if mcursor.rowcount != 1:
    print 'Updating mesosite resulted in %s rows modified' % (icursor.rowcount,)

mcursor.close()
MESOSITE.commit()
