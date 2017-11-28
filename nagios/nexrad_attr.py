"""Nagios check to make sure we have NEXRAD attribute data"""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis', user='nobody')
    pcursor = pgconn.cursor()

    pcursor.execute("""
        select count(*) from nexrad_attributes WHERE
        valid > now() - '30 minutes'::interval
    """)
    row = pcursor.fetchone()
    count = row[0]

    msg = "L3 NEXRAD attr count %s" % (count, )
    if count > 2:
        print('OK - %s |count=%s;2;1;0' % (msg, count))
        sys.exit(0)
    elif count > 1:
        print('OK - %s |count=%s;2;1;0' % (msg, count))
        sys.exit(1)
    else:
        print('CRITICAL - %s |count=%s;2;1;0' % (msg, count))
        sys.exit(2)


if __name__ == '__main__':
    main()
