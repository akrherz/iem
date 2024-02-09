"""Clean out MOS.

Run from `RUN_2AM.sh` script.
"""

from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    pgconn = get_dbconn("mos")
    cursor = pgconn.cursor()
    cursor.execute(
        "DELETE from alldata where model = 'LAV' and "
        "extract(hour from runtime at time zone 'UTC') not in (0, 6, 12, 18) "
        "and runtime > now() - '31 days'::interval and "
        "runtime < now() - '7 days'::interval"
    )
    if cursor.rowcount == 0:
        LOG.warning("Zero LAV rows deleted from MOS database?")
    cursor.execute(
        "DELETE from alldata where model in ('NBS', 'NBE') and "
        "extract(hour from runtime at time zone 'UTC') not in (1, 7, 13, 19) "
        "and runtime > now() - '31 days'::interval and "
        "runtime < now() - '7 days'::interval"
    )
    if cursor.rowcount == 0:
        LOG.warning("Zero NBM rows deleted from MOS database?")
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
