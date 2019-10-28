"""
 Measure how fast the ASOS database is responding to queries for data!
"""
from __future__ import print_function
import sys
import datetime
from pyiem.util import get_dbconn


def check():
    """Do the check"""
    pgconn = get_dbconn("asos", user="nobody")
    icursor = pgconn.cursor()
    year = str(datetime.datetime.now().year)
    icursor.execute(
        """
    SELECT station, count(*), min(tmpf), max(tmpf)
    from t"""
        + year
        + """ WHERE station =
    (select id from stations where network ~* 'ASOS' and online and
    archive_begin < '1980-01-01'
    ORDER by random() ASC LIMIT 1) GROUP by station
    """
    )
    row = icursor.fetchone()
    if row is None:
        return "XXX", 0
    return row[0], row[1]


def main():
    """Go Main"""
    t0 = datetime.datetime.now()
    station, count = check()
    t1 = datetime.datetime.now()
    delta = (t1 - t0).seconds + float((t1 - t0).microseconds) / 1000000.0
    if delta < 5:
        print(
            ("OK - %.3f %s %s |qtime=%.3f;5;10;15")
            % (delta, station, count, delta)
        )
        return 0
    elif delta < 10:
        print(
            ("WARNING - %.3f %s %s |qtime=%.3f;5;10;15")
            % (delta, station, count, delta)
        )
        return 1
    print(
        ("CRITICAL - %.3f %s %s |qtime=%.3f;5;10;15")
        % (delta, station, count, delta)
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
