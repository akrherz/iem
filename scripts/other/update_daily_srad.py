"""Compute daily SRAD.

Run from: RUN_MIDNIGHT.sh
"""

from datetime import datetime, timedelta

import click
from pyiem.database import get_dbconn
from pyiem.util import logger, utc

LOG = logger()


@click.command()
@click.option(
    "--date",
    "dt",
    type=click.DateTime(),
    required=True,
    help="Date to process",
)
def main(dt: datetime):
    """Run for the given args."""
    sts = utc(dt.year, dt.month, dt.day, 6)  # close enough
    ets = sts + timedelta(hours=24)
    # Find obs
    other = get_dbconn("other")
    cursor = other.cursor()
    cursor.execute(
        "SELECT station, sum(srad * 60) / 1e6 from alldata where srad > 0 "
        "and valid >= %s and valid < %s GROUP by station",
        (sts, ets),
    )
    iem = get_dbconn("iem")
    for row in cursor:
        if row[1] > 40 or row[1] < 0:
            LOG.warning("rad %s for %s out of bounds", row[1], row[0])
            continue
        LOG.info("Setting %s to %s", row[0], row[1])
        icursor = iem.cursor()
        icursor.execute(
            """
            UPDATE summary s SET srad_mj = %s FROM stations t where
            t.id = %s and t.network = %s and s.iemid = t.iemid and
            s.day = %s
            """,
            (row[1], row[0], "OT", sts.date()),
        )
        if icursor.rowcount != 1:
            LOG.warning("Summary update failed for %s", row[0])
            icursor.close()
            continue
        icursor.close()
        iem.commit()


if __name__ == "__main__":
    main()
