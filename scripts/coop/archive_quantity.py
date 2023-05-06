""" Create a simple prinout of observation quanity in the database """
import datetime
import sys

import numpy as np
from pyiem.util import get_dbconn


class bcolors:
    """Another Hack"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def d(possible, actual):
    """Hack"""
    c1 = bcolors.ENDC
    if possible != actual:
        c1 = bcolors.FAIL
    return "%s%4.0f%s" % (c1, actual, bcolors.ENDC)


def main(argv):
    """Go Main Go"""
    now = datetime.datetime.utcnow()
    years = now.year - 1893 + 1
    counts = np.zeros((years, 12))

    pgconn = get_dbconn("coop")
    acursor = pgconn.cursor()

    stid = argv[1]
    acursor.execute(
        """SELECT year, month,
     count(*),
     sum(case when high is null then 0 else 1 end),
     sum(case when low is null then 0 else 1 end),
     sum(case when precip is null then 0 else 1 end)
     from alldata WHERE
     station = %s and year > 1892 GROUP by year, month""",
        (stid,),
    )

    idx = 2
    vname = "Counts"
    if len(argv) == 3:
        vname = argv[2]
        if vname == "high":
            idx = 3
        elif vname == "low":
            idx = 4
        elif vname == "precip":
            idx = 5

    for row in acursor:
        counts[int(row[0] - 1893), int(row[1] - 1)] = row[idx]

    print("Observation Count For %s [%s]" % (stid, vname))
    print("YEAR  JAN  FEB  MAR  APR  MAY  JUN  JUL  AUG  SEP  OCT  NOV  DEC")
    output = False
    for i in range(years):
        year = 1893 + i
        if year > now.year:
            continue
        if not output and np.max(counts[i, :]) == 0:
            continue
        output = True

        days = []
        for mo in range(1, 13):
            sts = datetime.datetime(year, mo, 1)
            ets = sts + datetime.timedelta(days=35)
            ets = ets.replace(day=1)
            days.append((ets - sts).days)

        print(
            ("%s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s %4s")
            % (
                year,
                d(days[0], counts[i, 0]),
                d(days[1], counts[i, 1]),
                d(days[2], counts[i, 2]),
                d(days[3], counts[i, 3]),
                d(days[4], counts[i, 4]),
                d(days[5], counts[i, 5]),
                d(days[6], counts[i, 6]),
                d(days[7], counts[i, 7]),
                d(days[8], counts[i, 8]),
                d(days[9], counts[i, 9]),
                d(days[10], counts[i, 10]),
                d(days[11], counts[i, 11]),
            )
        )


if __name__ == "__main__":
    main(sys.argv)
