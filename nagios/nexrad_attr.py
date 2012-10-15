"""
 Nagios check to make sure we have NEXRAD attribute data
"""
import sys
import os
import psycopg2

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

pcursor.execute("""
 select count(*) from nexrad_attributes WHERE 
 valid > now() - '30 minutes'::interval
""")
row = pcursor.fetchone()
count = row[0]

if count > 30:
    print 'OK - attrs %s |count=%s;15;30;0' % (count, count)
    sys.exit(0)
elif count > 15:
    print 'OK - attrs %s |count=%s;15;30;0' % (count, count)
    sys.exit(1)
else:
    print 'CRITICAL - attrs %s |count=%s;15;30;0' % (count, count)
    sys.exit(2)