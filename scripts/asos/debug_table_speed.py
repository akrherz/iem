"""Debug printout of partitioned table speed within ASOS database"""
from __future__ import print_function
import datetime

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    maxt = 0
    for yr in range(1928, datetime.datetime.now().year + 1):
        sts = datetime.datetime.now()
        cursor.execute(
            """
            SELECT count(*) from t"""
            + str(yr)
            + """
            WHERE station = %s
        """,
            ("DSM",),
        )
        row = cursor.fetchone()
        ets = datetime.datetime.now()
        secs = (ets - sts).total_seconds()
        print(
            "%s %6i %8.4f%s"
            % (yr, row[0], secs, " <-- " if secs > maxt else "")
        )
        maxt = max([secs, maxt])


if __name__ == "__main__":
    main()
