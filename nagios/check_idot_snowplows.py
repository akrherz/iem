"""
 Nagios check to see how much snowplow data we are currently ingesting
"""
import sys
import os
import psycopg2

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

pcursor.execute("""
 select count(*) from idot_snowplow_current WHERE 
 valid > now() - '30 minutes'::interval
""")
row = pcursor.fetchone()
count = row[0]

if count > 2:
    print 'OK - snowplows %s |count=%s;2;1;0' % (count, count)
    sys.exit(0)
elif count > 1:
    print 'OK - snowplows %s |count=%s;2;1;0' % (count, count)
    sys.exit(1)
else:
    print 'CRITICAL - snowplows %s |count=%s;2;1;0' % (count, count)
    sys.exit(2)