"""
Fuzzy math to get the right timestamp

if 15, we want 00
if 45, we want 30
"""
from __future__ import print_function
import datetime
import sys


def main(argv):
    """Go Main Go"""
    gmt = datetime.datetime.utcnow()

    cycle = sys.argv[1]

    if cycle == "15":
        gmt = gmt.replace(minute=0)
    else:
        gmt -= datetime.timedelta(hours=1)
        gmt = gmt.replace(minute=30)

    print(gmt.strftime(argv[2]))


if __name__ == "__main__":
    main(sys.argv)
