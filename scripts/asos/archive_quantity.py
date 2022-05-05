""" Create a simple prinout of observation quanity in the database """
import sys

import datetime
import numpy as np
from pyiem.util import get_dbconn

BASEYEAR = 1928


class bcolors:
    """Kind of hacky"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def d(hits, total):
    """another hack"""
    if total == 0:
        return " N/A"
    val = hits / float(total)
    c1 = bcolors.ENDC
    if val > 0.5:
        c1 = bcolors.FAIL
    return "%s%.2f%s" % (c1, val, bcolors.ENDC)


def main(argv):
    """Go Main Go"""
    now = datetime.datetime.utcnow()
    years = int(now.year - 1928 + 1)
    counts = np.zeros((years, 12))
    mslp = np.zeros((years, 12))
    metar = np.zeros((years, 12))

    pgconn = get_dbconn("asos", user="nobody")
    acursor = pgconn.cursor()

    stid = argv[1]
    acursor.execute(
        """
        SELECT extract(year from valid) as yr,
        extract(month from valid) as mo, count(*),
        sum(case when mslp is null or mslp < 1 then 1 else 0 end),
        sum(case when metar is null or metar = '' then 1 else 0 end)
        from alldata WHERE
        station = %s GROUP by yr, mo ORDER by yr ASC, mo ASC
    """,
        (stid,),
    )

    for row in acursor:
        counts[int(row[0] - BASEYEAR), int(row[1] - 1)] = row[2]
        mslp[int(row[0] - BASEYEAR), int(row[1] - 1)] = row[3]
        metar[int(row[0] - BASEYEAR), int(row[1] - 1)] = row[4]

    print(f"Observation Count For {stid}")
    print("YEAR  JAN  FEB  MAR  APR  MAY  JUN  JUL  AUG  SEP  OCT  NOV  DEC")
    output = False
    for i in range(years):
        year = BASEYEAR + i
        if year > now.year:
            continue
        if not output and np.max(counts[i, :]) == 0:
            continue
        output = True

        if len(argv) < 3:
            print(
                ("%s %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i %4i")
                % (
                    year,
                    counts[i, 0],
                    counts[i, 1],
                    counts[i, 2],
                    counts[i, 3],
                    counts[i, 4],
                    counts[i, 5],
                    counts[i, 6],
                    counts[i, 7],
                    counts[i, 8],
                    counts[i, 9],
                    counts[i, 10],
                    counts[i, 11],
                )
            )
        else:
            if argv[2] == "metar":
                data = metar
            else:
                data = mslp
            print(
                ("%s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s")
                % (
                    year,
                    d(data[i, 0], counts[i, 0]),
                    d(data[i, 1], counts[i, 1]),
                    d(data[i, 2], counts[i, 2]),
                    d(data[i, 3], counts[i, 3]),
                    d(data[i, 4], counts[i, 4]),
                    d(data[i, 5], counts[i, 5]),
                    d(data[i, 6], counts[i, 6]),
                    d(data[i, 7], counts[i, 7]),
                    d(data[i, 8], counts[i, 8]),
                    d(data[i, 9], counts[i, 9]),
                    d(data[i, 10], counts[i, 10]),
                    d(data[i, 11], counts[i, 11]),
                )
            )


if __name__ == "__main__":
    main(sys.argv)
