"""
 Nagios check to see how much snowplow data we are currently ingesting
"""
import sys
import psycopg2

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

pcursor.execute("""
select sum(case when valid > now() - '30 minutes'::interval then 1 else 0 end),
 sum(case when valid > now() - '1 day'::interval then 1 else 0 end)
 from idot_snowplow_current
""")
row = pcursor.fetchone()
count = row[0]
daycount = row[1]

if daycount > 2:
    print(('OK - snowplows %s/%s |count=%s;2;1;0 daycount=%s;2;1;0'
           ) % (count, daycount, count, daycount))
    sys.exit(0)
elif daycount > 1:
    print(('OK - snowplows %s/%s |count=%s;2;1;0 daycount=%s;2;1;0'
           ) % (count, daycount, count, daycount))
    sys.exit(1)
else:
    print(('CRITICAL - snowplows %s/%s |count=%s;2;1;0 daycount=%s;2;1;0'
           ) % (count, daycount, count, daycount))
    sys.exit(2)
