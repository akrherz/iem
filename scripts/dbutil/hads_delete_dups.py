"""
 Our HADS database gets loaded up with duplicates, this cleans it up.

 called from RUN_MIDNIGHT.sh
"""
import datetime
import sys

from pyiem.util import get_dbconn, utc, logger

LOG = logger()


def query(sql, args=None):
    """
    Do a query and make it atomic
    """
    pgconn = get_dbconn("hads")
    hcursor = pgconn.cursor()
    sts = datetime.datetime.now()
    hcursor.execute("set work_mem='16GB'")
    hcursor.execute(sql, args if args is not None else [])
    ets = datetime.datetime.now()
    LOG.debug(
        "%7s [%8.4fs] %s", hcursor.rowcount, (ets - sts).total_seconds(), sql
    )
    hcursor.close()
    pgconn.commit()


def workflow(valid):
    """Do the work for this date, which is set to 00 UTC"""
    tbl = "raw%s" % (valid.strftime("%Y_%m"),)

    # make sure our tmp table does not exist
    query("DROP TABLE IF EXISTS tmp")
    # Extract unique obs to special table
    sql = (
        f"CREATE table tmp as select distinct * from {tbl} "
        "WHERE valid BETWEEN %s and %s"
    )
    args = (valid, valid + datetime.timedelta(hours=24))
    query(sql, args)

    # Delete them all!
    sql = f"delete from {tbl} WHERE valid BETWEEN %s and %s"
    query(sql, args)

    # Insert from special table
    sql = f"INSERT into {tbl} SELECT * from tmp"
    query(sql)

    sql = "DROP TABLE IF EXISTS tmp"
    query(sql)


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        utcnow = utc(int(argv[1]), int(argv[2]), int(argv[3]))
        workflow(utcnow)
        return
    utcnow = utc().replace(hour=0, minute=0, second=0, microsecond=0)
    # Run for 'yesterday' and 35 days ago
    for day in [1, 35]:
        workflow(utcnow - datetime.timedelta(days=day))


if __name__ == "__main__":
    # See how we are called
    main(sys.argv)
