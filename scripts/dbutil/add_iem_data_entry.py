"""
 Main script that adds a site into the appropriate tables
 called from SYNC_STATIONS.sh
"""
from __future__ import print_function
import datetime
import psycopg2.extras
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor2 = pgconn.cursor()

    # Find sites that are online and not metasites that are not in the current
    # table!
    icursor.execute(
        """
     select s.iemid, id, network from stations s LEFT JOIN current c
     ON c.iemid = s.iemid where c.iemid is null and s.online and
     not s.metasite
    """
    )

    now = datetime.datetime.now()

    for row in icursor:
        print(
            ("Add iemdb current: ID: %10s NETWORK: %s")
            % (row["id"], row["network"])
        )

        tbl = "summary_%s" % (now.year,)
        icursor2.execute(
            """
            INSERT into %s (day, iemid) VALUES ('TODAY', %s)
            """
            % (tbl, row["iemid"])
        )

        tbl = "summary_%s" % ((now + datetime.timedelta(days=1)).year,)
        icursor2.execute(
            """INSERT into %s ( day, iemid)
              VALUES ( 'TOMORROW', %s) """
            % (tbl, row["iemid"])
        )
        tbl = "current"
        icursor2.execute(
            """INSERT into %s ( valid, iemid)
              VALUES ('1980-01-01', %s) """
            % (tbl, row["iemid"])
        )

    icursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
