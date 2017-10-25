"""Check autoplot stats"""
from __future__ import print_function
import sys

import psycopg2


def main():
    """Go Main Go"""
    pgconn = psycopg2.connect(database='mesosite', host='iemdb',
                              user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""
        select count(*), avg(timing) from autoplot_timing
        where valid > now() - '4 hours'::interval
    """)
    (count, speed) = cursor.fetchone()
    speed = 0 if speed is None else speed

    print(("Autoplot cnt:%s speed:%.2f | COUNT=%s;; SPEED=%.3f;;"
           ) % (count, speed, count, speed))
    sys.exit(0)


if __name__ == '__main__':
    main()
