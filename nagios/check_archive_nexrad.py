"""
Make sure we have archived N0R so that things do not freak out!
"""
from __future__ import print_function
import datetime
import sys
import os


def main(argv):
    """Do Great Things!"""
    prod = argv[1]
    now = datetime.datetime.utcnow()
    now = now - datetime.timedelta(minutes=now.minute % 5)
    base = now

    miss = []
    for _ in range(12):
        fn = now.strftime(
            (
                "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/"
                + prod
                + "_%Y%m%d%H%M.png"
            )
        )
        if not os.path.isfile(fn):
            miss.append(now.strftime("%Y%m%d_%H%M"))
        now -= datetime.timedelta(minutes=5)

    if not miss:
        print("OK")
        return 0
    print(
        "CRITICAL - %s archive miss N0R %s"
        % (base.strftime("%d_%H%M"), ", ".join(miss))
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
