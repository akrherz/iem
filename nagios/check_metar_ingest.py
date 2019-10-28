"""
 Check how much METAR data we have
"""
import sys

from pyiem.util import get_dbconn


def check():
    """Do the check"""
    pgconn = get_dbconn("iem", host=sys.argv[1], user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        """SELECT count(*) from current c JOIN stations s on
    (s.iemid = c.iemid)
    WHERE valid > now() - '75 minutes'::interval and network ~* 'ASOS'"""
    )
    row = icursor.fetchone()

    return row[0]


def main():
    """Go Main"""
    count = check()
    if count > 3000:
        print("OK - %s count |count=%s;1000;5000;10000" % (count, count))
        return 0
    elif count > 2000:
        print("WARNING - %s count |count=%s;1000;5000;10000" % (count, count))
        return 1
    else:
        print("CRITICAL - %s count |count=%s;1000;5000;10000" % (count, count))
        return 2


if __name__ == "__main__":
    sys.exit(main())
