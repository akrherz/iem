"""
 Nagios check to see how much snowplow data we are currently ingesting
"""
from __future__ import print_function
import sys
import datetime

import psycopg2


def main():
    """Do Great Things"""
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    pcursor = pgconn.cursor()

    pcursor.execute("""
        select sum(case when valid > now() - '30 minutes'::interval
            then 1 else 0 end),
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
        # Don't error in the summer
        retcode = (2 if datetime.date.today().month not in (5, 6, 7, 8, 9, 10)
                   else 0)
        sys.exit(retcode)


if __name__ == '__main__':
    main()
