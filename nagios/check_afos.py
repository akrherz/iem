"""
 Check how much AFOS data we are ingesting
"""
import sys
from pyiem.util import get_dbconn


def check():
    """Do the check"""
    pgconn = get_dbconn("afos", user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        """SELECT count(*) from products
    WHERE entered > now() - '1 hour'::interval"""
    )
    row = icursor.fetchone()

    return row[0]


def main():
    """Go Main."""
    count = check()
    if count > 1000:
        print("OK - %s count |count=%s;100;500;1000" % (count, count))
        return 0
    elif count > 500:
        print("WARNING - %s count |count=%s;100;500;1000" % (count, count))
        return 1
    else:
        print("CRITICAL - %s count |count=%s;100;500;1000" % (count, count))
        return 2


if __name__ == "__main__":
    sys.exit(main())
