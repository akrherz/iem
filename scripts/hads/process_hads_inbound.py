"""Moved staged SHEF data into long term tables.

Note, we do not want to do TRUNCATE here to do ugly locking that happens and
which can jam things up badly when we are doing upgrades, etc.
"""

import pytz
from pyiem.util import get_dbconn, logger, utc

LOG = logger()


def main():
    """Do things"""
    ceiling = utc()
    pgconn = get_dbconn("hads")
    cursor2 = pgconn.cursor()
    cursor = pgconn.cursor()
    cursor.execute(
        "INSERT into raw_inbound_tmp SELECT distinct station, valid, "
        "key, value, depth, unit_convention, qualifier, dv_interval "
        "from raw_inbound WHERE updated < %s",
        (ceiling,),
    )
    LOG.debug("inserted %s rows into tmp", cursor.rowcount)
    cursor.execute("delete from raw_inbound where updated < %s", (ceiling,))
    LOG.debug("removed %s rows from inbound", cursor.rowcount)
    cursor.close()
    pgconn.commit()
    cursor = pgconn.cursor()
    # Sometimes we get old data that should not be in the database.
    cursor.execute(
        "SELECT station, valid at time zone 'UTC', key, value, depth, "
        "unit_convention, qualifier, dv_interval from raw_inbound_tmp "
        "WHERE valid > '2002-01-01'"
    )
    for row in cursor:
        table = f"raw{row[1]:%Y_%m}"
        ts = row[1].replace(tzinfo=pytz.utc)
        cursor2.execute(
            f"INSERT into {table} "
            "(station, valid, key, value, depth, unit_convention, "
            "qualifier, dv_interval) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (row[0], ts, *row[2:]),
        )
    if cursor.rowcount == 0:
        LOG.info("found no data to insert...")
    cursor.execute("delete from raw_inbound_tmp")
    LOG.debug("removed %s rows from tmp", cursor.rowcount)
    cursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
