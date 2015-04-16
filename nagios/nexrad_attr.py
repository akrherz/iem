"""Nagios check to make sure we have NEXRAD attribute data"""
import sys
import psycopg2

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

pcursor.execute("""
    select count(*) from nexrad_attributes WHERE
    valid > now() - '30 minutes'::interval
""")
row = pcursor.fetchone()
count = row[0]

msg = "L3 NEXRAD attr count %s" % (count, )
if count > 2:
    print 'OK - %s |count=%s;2;1;0' % (msg, count)
    sys.exit(0)
elif count > 1:
    print 'OK - %s |count=%s;2;1;0' % (msg, count)
    sys.exit(1)
else:
    print 'CRITICAL - %s |count=%s;2;1;0' % (msg, count)
    sys.exit(2)
