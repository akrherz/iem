"""
 Nagios check to see how much snowplow data we are currently ingesting
"""
from __future__ import print_function
import sys
import datetime

from pyiem.util import get_dbconn


def main():
    """Do Great Things"""
    pgconn = get_dbconn("postgis", user="nobody")
    pcursor = pgconn.cursor()

    pcursor.execute(
        """
        select sum(case when valid > now() - '30 minutes'::interval
            then 1 else 0 end),
         sum(case when valid > now() - '1 day'::interval then 1 else 0 end)
         from idot_snowplow_current
    """
    )
    row = pcursor.fetchone()
    count = row[0]
    daycount = row[1]

    if datetime.date.today().month in (5, 6, 7, 8, 9, 10):
        print(
            ("OK - snowplows %s/%s |count=%s;2;1;0 daycount=%s;2;1;0")
            % (count, daycount, count, daycount)
        )
        sys.exit(0)
    elif daycount > 2:
        print(
            ("OK - snowplows %s/%s |count=%s;2;1;0 daycount=%s;2;1;0")
            % (count, daycount, count, daycount)
        )
        sys.exit(0)
    elif daycount > 1:
        print(
            ("OK - snowplows %s/%s |count=%s;2;1;0 daycount=%s;2;1;0")
            % (count, daycount, count, daycount)
        )
        sys.exit(1)
    print(
        ("CRITICAL - snowplows %s/%s |count=%s;2;1;0 daycount=%s;2;1;0")
        % (count, daycount, count, daycount)
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
