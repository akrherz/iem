"""Cull old website_telemetry data

called from RUN_2AM.sh
"""

from datetime import datetime, timedelta

from pyiem.database import get_dbconnc
from pyiem.util import logger

LOG = logger()


def main():
    """Clean AFOS and friends"""
    pgconn, cursor = get_dbconnc("mesosite")
    # yesterday at 12 AM Central
    sts = datetime.now() - timedelta(days=1)
    sts = sts.replace(hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("DELETE from website_telemetry WHERE valid < %s", (sts,))
    if cursor.rowcount == 0:
        LOG.warning("Found no website_telemetry entries to delete")
    LOG.info("deleted %s rows", cursor.rowcount)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
