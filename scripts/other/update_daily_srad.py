"""Compute daily SRAD.

Run from: RUN_MIDNIGHT.sh
"""

from datetime import datetime, timedelta

import click
from pyiem.database import get_sqlalchemy_conn, sql_helper
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
    with (
        get_sqlalchemy_conn("other") as oconn,
        get_sqlalchemy_conn("iem") as iconn,
    ):
        res = oconn.execute(
            sql_helper("""
    SELECT station, sum(srad * 60) / 1e6 from alldata where srad > 0
    and valid >= :sts and valid < :ets GROUP by station"""),
            {"sts": sts, "ets": ets},
        )
        for row in res:
            if row[1] > 40 or row[1] < 0:
                LOG.warning("rad %s for %s out of bounds", row[1], row[0])
                continue
            LOG.info("Setting %s to %s", row[0], row[1])
            res2 = iconn.execute(
                sql_helper(
                    """
                UPDATE {table} s SET srad_mj = :rad FROM stations t where
                t.id = :sid and t.network = 'OT' and s.iemid = t.iemid and
                s.day = :day
                """,
                    table=f"summary_{sts:Y}",
                ),
                {"rad": row[1], "sid": row[0], "day": sts.date()},
            )
            if res2.rowcount != 1:
                LOG.warning("Summary update failed for %s", row[0])
                continue
            iconn.commit()


if __name__ == "__main__":
    main()
