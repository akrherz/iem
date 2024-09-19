"""
Our HADS database gets loaded up with duplicates, this cleans it up.

called from RUN_MIDNIGHT.sh for yesterday and 35 days ago
"""

from datetime import datetime, timedelta, timezone

import click
from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def query(sql, args=None):
    """
    Do a query and make it atomic
    """
    pgconn = get_dbconn("hads")
    hcursor = pgconn.cursor()
    sts = datetime.now()
    hcursor.execute("set work_mem='16GB'")
    hcursor.execute(sql, args if args is not None else [])
    ets = datetime.now()
    LOG.info(
        "%7s [%8.4fs] %s", hcursor.rowcount, (ets - sts).total_seconds(), sql
    )
    hcursor.close()
    pgconn.commit()


def workflow(valid):
    """Do the work for this date, which is set to 00 UTC"""
    tbl = f"raw{valid:%Y_%m}"

    # make sure our tmp table does not exist
    query("DROP TABLE IF EXISTS tmp")
    # Extract unique obs to special table
    sql = (
        f"CREATE table tmp as select distinct * from {tbl} "
        "WHERE valid BETWEEN %s and %s"
    )
    args = (valid, valid + timedelta(hours=24))
    query(sql, args)

    # Delete them all!
    sql = f"delete from {tbl} WHERE valid BETWEEN %s and %s"
    query(sql, args)

    # Insert from special table
    sql = f"INSERT into {tbl} SELECT * from tmp"
    query(sql)

    sql = "DROP TABLE IF EXISTS tmp"
    query(sql)


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), required=True, help="Specific date"
)
def main(dt: datetime):
    """Go Main Go"""
    valid = dt.replace(tzinfo=timezone.utc)
    workflow(valid)


if __name__ == "__main__":
    # See how we are called
    main()
