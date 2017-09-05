"""Create WMS-T database entries as necessary
"""
from __future__ import print_function
import datetime
import sys

import psycopg2


def main():
    """Go Main!"""
    pgconn = psycopg2.connect(database='postgis', host='iemdb')
    cursor = pgconn.cursor()

    now = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                            int(sys.argv[3]), 0, 0)
    ets = now + datetime.timedelta(days=1)

    product = sys.argv[4].lower()
    table = 'nexrad_%s_tindex' % (product,)

    while now < ets:
        cursor.execute("""SELECT * from """+table+""" WHERE datetime = %s""",
                       (now,))

        if cursor.rowcount == 0:
            print('Insert %s' % (now,))
            fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/"
                               "uscomp/"+product+"_%Y%m%d%H%M.png"))
            cursor.execute("""
            INSERT into """+table+""" (datetime, filepath, the_geom) VALUES
            (%s, %s,
            'SRID=4326;
             MULTIPOLYGON(((-126 50,-66 50,-66 24,-126 24,-126 50)))')
            """, (now, fn))

        now += datetime.timedelta(minutes=5)

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == '__main__':
    main()
