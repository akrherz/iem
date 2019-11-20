"""
 Main script that adds a site into the appropriate tables
 called from SYNC_STATIONS.sh
"""
import datetime

import psycopg2.extras
from pyiem.util import get_dbconn, logger

LOG = logger()


def add_summary(cursor, date, iemid):
    """Add a summary entry for the given date."""
    table = "summary_%s" % (date.year,)
    cursor.execute(
        """
        SELECT iemid from """
        + table
        + """ WHERE day = %s and iemid = %s
    """,
        (date, iemid),
    )
    if cursor.rowcount == 1:
        LOG.info("%s entry already exists for date %s", table, date)
        return
    cursor.execute(
        """
        INSERT into """
        + table
        + """ (day, iemid) values (%s, %s)
    """,
        (date, iemid),
    )


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
        LOG.info(
            "Add iemdb current: ID: %10s NETWORK: %s",
            row["id"],
            row["network"],
        )

        for date in [now, now - datetime.timedelta(days=1)]:
            add_summary(icursor2, date, row["iemid"])
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
