""" Create a simple prinout of observation quanity in the database """
import datetime
import sys

import numpy as np
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    now = datetime.datetime.utcnow()
    years = now.year - 2000 + 1
    counts = np.zeros((years, 12))

    pgconn = get_dbconn("radar")
    acursor = pgconn.cursor()

    stid = sys.argv[1]

    class bcolors:
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"

    acursor.execute(
        """
        SELECT extract(year from valid) as year,
        extract(month from valid) as month,
        count(*) from nexrad_attributes_log WHERE
        nexrad = %s GROUP by year, month
    """,
        (stid,),
    )

    for row in acursor:
        counts[int(row[0] - 2000), int(row[1] - 1)] = row[2]

    def d(possible, actual):
        c1 = bcolors.ENDC
        if possible < actual:
            c1 = bcolors.FAIL
        return "%s%5.0f%s" % (c1, actual, bcolors.ENDC)

    print("Observation Count For %s" % (stid,))
    print(
        "YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP"
        "    OCT    NOV    DEC"
    )
    output = False
    for i in range(years):
        year = 2000 + i
        if year > now.year:
            continue
        if not output and np.max(counts[i, :]) == 0:
            continue
        output = True

        print(
            "%s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s"
            % (
                year,
                d(100, counts[i, 0]),
                d(100, counts[i, 1]),
                d(100, counts[i, 2]),
                d(100, counts[i, 3]),
                d(100, counts[i, 4]),
                d(100, counts[i, 5]),
                d(100, counts[i, 6]),
                d(100, counts[i, 7]),
                d(100, counts[i, 8]),
                d(100, counts[i, 9]),
                d(100, counts[i, 10]),
                d(100, counts[i, 11]),
            )
        )


if __name__ == "__main__":
    main()
