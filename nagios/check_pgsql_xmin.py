"""
  Return the maximum xmin in the database, having too large of a value leads to
  bad things and eventual database not accepting new writes.  I had to lower
  the default postgresql setting from 200 mil to 180 mil as the database does
  lots of writes and autovac sometimes can not keep up.
"""
from __future__ import print_function
import sys
from pyiem.util import get_dbconn


def check(dbname):
    """Do the database check."""
    pgconn = get_dbconn(dbname, user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        """
        SELECT datname, age(datfrozenxid) FROM pg_database
        ORDER by age DESC LIMIT 1
    """
    )
    row = icursor.fetchone()

    return row


def main(argv):
    """Go Main Go."""
    dbname, count = check(argv[1])
    if count < 191000000:
        print(
            "OK - %s %s |count=%s;191000000;195000000;220000000"
            % (count, dbname, count)
        )
        retval = 0
    elif count < 195000000:
        print(
            ("WARNING - %s %s |count=%s;191000000;195000000;220000000")
            % (count, dbname, count)
        )
        retval = 1
    else:
        print(
            ("CRITICAL - %s %s |count=%s;191000000;195000000;220000000")
            % (count, dbname, count)
        )
        retval = 2
    return retval


if __name__ == "__main__":
    sys.exit(main(sys.argv))
