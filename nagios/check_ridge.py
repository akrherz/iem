"""
 Make sure we have current RIDGE imagery
"""
from __future__ import print_function
import os
import sys
import stat
import datetime

SAMPLES = ["DVN", "GRK", "ABC", "DTX", "HTX", "LOT", "TLX"]


def check():
    """Check things."""
    now = datetime.datetime.now()
    count = []
    for nexrad in SAMPLES:
        fn = "/home/ldm/data/gis/images/4326/ridge/%s/N0Q_0.png" % (nexrad,)
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400.0 + (now - ts).seconds
        if diff > 600:
            count.append(nexrad)
    return count


def main():
    """Go Main Go."""
    badcount = check()
    msg = "%s/%s outage %s" % (len(badcount), len(SAMPLES), ",".join(badcount))
    if len(badcount) < 3:
        print("OK - %s" % (msg,))
        status = 0
    elif len(badcount) < 4:
        print("WARNING - %s" % (msg,))
        status = 1
    else:
        print("CRITICAL - %s" % (msg,))
        status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())
