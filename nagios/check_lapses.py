"""Make sure we are producing webcam lapses!"""
from __future__ import print_function
import os
import sys
import stat
import datetime

BASEDIR = "/mesonet/share/lapses/auto"


def check():
    """Do the actual check"""
    good = 0
    now = datetime.datetime.now()
    for filename in os.listdir(BASEDIR):
        fn = "%s/%s" % (BASEDIR, filename)
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400.0 + (now - ts).seconds
        if diff < 86400:
            good += 1
    return good


def main():
    """Go Main Go."""
    good = check()
    msg = "%s good lapses" % (good,)
    if good > 30:
        print("OK - %s" % (msg,))
        return 0
    print("CRITICAL - %s" % (msg,))
    return 2


if __name__ == "__main__":
    sys.exit(main())
