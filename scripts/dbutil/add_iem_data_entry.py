"""
 Main script that adds a site into the appropriate tables
 called from SYNC_STATIONS.sh
"""
import datetime

from pyiem.database import get_dbconnc
from pyiem.util import logger

LOG = logger()


def add_summary(cursor, date, iemid):
    """Add a summary entry for the given date."""
    cursor.execute(
        "SELECT iemid from summary WHERE day = %s and iemid = %s",
        (date, iemid),
    )
    if cursor.rowcount == 1:
        LOG.info("Entry already exists for date %s", date)
        return
    cursor.execute(
        "INSERT into summary (day, iemid) values (%s, %s)", (date, iemid)
    )


def main():
    """Go Main Go"""
    pgconn, icursor = get_dbconnc("iem")
    icursor2 = pgconn.cursor()

    # Find sites that are online and not metasites that are not in the current
    # table!
    icursor.execute(
        "select s.iemid, id, network from stations s LEFT JOIN current c "
        "ON c.iemid = s.iemid where c.iemid is null and s.online and "
        "not s.metasite"
    )

    now = datetime.datetime.now()

    for row in icursor:
        LOG.info(
            "Add iemdb current: ID: %10s NETWORK: %s",
            row["id"],
            row["network"],
        )

        for valid in [now, now - datetime.timedelta(days=1)]:
            add_summary(icursor2, valid.date(), row["iemid"])
        icursor2.execute(
            "INSERT into current (valid, iemid) VALUES ('1980-01-01', %s)",
            (row["iemid"],),
        )

    icursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
