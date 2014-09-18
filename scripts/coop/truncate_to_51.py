"""
 Remove any old data for a given station for dates older than 1951
"""
import psycopg2
import sys

PGCONN = psycopg2.connect(database='coop', host='iemdb')
cursor = PGCONN.cursor()

station = sys.argv[1]
table = "alldata_%s" % (station[:2],)
cursor.execute("""DELETE from """+table+""" WHERE station = %s
 and day < '1951-01-01' """, (station,))

print 'Deleted %s rows from table %s for station %s' % (cursor.rowcount,
                                                        table, station)

cursor.close()
PGCONN.commit()