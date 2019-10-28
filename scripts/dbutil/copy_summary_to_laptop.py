"""Bring the summary table entries to my laptop, please!"""
from __future__ import print_function
import sys
import datetime
import psycopg2.extras
from pyiem.util import get_dbconn


def main(argv):
    """Go Main"""
    iemdb = get_dbconn("iem")
    icursor = iemdb.cursor()

    remotedb = get_dbconn("iem", host="129.186.185.33", user="nobody")
    cur = remotedb.cursor(cursor_factory=psycopg2.extras.DictCursor)

    date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))

    cur.execute("""SELECT * from summary where day = %s""", (date,))

    table = "summary_%s" % (date.year,)
    for row in cur:
        icursor.execute(
            """INSERT into """
            + table
            + """ (iemid, day, max_tmpf,
        min_tmpf, pday, snow, snowd) values (%(iemid)s, %(day)s, %(max_tmpf)s,
        %(min_tmpf)s, %(pday)s, %(snow)s, %(snowd)s)
        """,
            row,
        )

    icursor.close()
    iemdb.commit()
    iemdb.close()


if __name__ == "__main__":
    main(sys.argv)
