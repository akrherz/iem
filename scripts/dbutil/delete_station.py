"""Delete a station and all references to it!"""
import psycopg2
import sys
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()

if len(sys.argv) != 3:
    print 'Usage: python remove_realtime.py NETWORK SID'
    sys.exit()

network = sys.argv[1]
station = sys.argv[2]

for table in ['current', 'summary']:
    icursor.execute("""
     DELETE from %s where
     iemid = (select iemid from stations where id = '%s' and network = '%s')
    """ % (table, station, network))
    if icursor.rowcount != 1:
        print(('Updating table: %s resulted in %s rows removed'
               ) % (table, icursor.rowcount))


icursor.close()
IEM.commit()

mcursor.execute("""
    DELETE from stations where id = '%s' and network = '%s'
""" % (station, network))
if mcursor.rowcount != 1:
    print(('Updating mesosite resulted in %s rows removed'
           ) % (icursor.rowcount, ))

mcursor.close()
MESOSITE.commit()
