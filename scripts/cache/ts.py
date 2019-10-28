""" Set GIS Satellite data! :)"""

# 15 after scan produced at 45 after
# 45 after scan produced at 15 after
from __future__ import print_function
import datetime
import sys


def main(argv):
    """Go Main Go"""
    now = datetime.datetime.utcnow()

    cycle = argv[1]

    if cycle == "15":
        now = now.replace(minute=15)
    else:
        now -= datetime.timedelta(hours=1)
        now = now.replace(minute=45)

    print(now.strftime(argv[2]))


if __name__ == "__main__":
    main(sys.argv)
