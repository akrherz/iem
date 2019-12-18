"""
 Make sure our nexrad files are current!
"""
from __future__ import print_function
import os
import sys
import stat
import datetime

SAMPLES = ["KDMX", "KAMA", "KLWX", "KFFC", "KBMX", "KBGM", "KCLE"]


def check():
    """Check things please"""
    now = datetime.datetime.now()
    count = []
    for nexrad in SAMPLES:
        fn = "/mnt/level2/raw/%s/dir.list" % (nexrad,)
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400.0 + (now - ts).seconds
        if diff > 300:
            count.append(nexrad)
    return count


def main():
    """Go Main Go"""
    badcount = check()
    msg = "%s/%s outage %s" % (len(badcount), len(SAMPLES), ",".join(badcount))
    if len(badcount) < 3:
        print("OK - %s" % (msg,))
        sys.exit(0)
    elif len(badcount) < 4:
        print("WARNING - %s" % (msg,))
        sys.exit(1)
    else:
        print("CRITICAL - %s" % (msg,))
        sys.exit(2)


if __name__ == "__main__":
    main()
