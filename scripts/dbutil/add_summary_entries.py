"""Initialize entries in the IEM summary table"""

import datetime
import sys

from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def main(argv):
    """Go Main Go"""
    (network, station, year, month, day) = argv[1:]
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    cursor.execute(
        """
    SELECT s.iemid, min(day)
    from summary s JOIN stations t on (s.iemid = t.iemid)
    WHERE t.id = %s and t.network = %s GROUP by s.iemid
    """,
        (station, network),
    )
    if cursor.rowcount == 0:
        LOG.info("ABORT: found no database entries for station")
        return
    (iemid, maxday) = cursor.fetchone()
    day = datetime.date(int(year), int(month), int(day))
    added = 0
    while day < maxday:
        added += 1
        cursor.execute(
            "INSERT into summary (iemid, day) VALUES (%s, %s)", (iemid, day)
        )
        day += datetime.timedelta(days=1)
    LOG.info("Added %s rows for station %s[%s]", added, station, network)

    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main(sys.argv)
