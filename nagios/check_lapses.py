"""Make sure we are producing webcam lapses!"""
import os
import sys
import stat
import datetime
BASEDIR = "/mesonet/share/lapses/auto"


def check():
    good = 0
    now = datetime.datetime.now()
    for filename in os.listdir(BASEDIR):
        fn = "%s/%s" % (BASEDIR, filename)
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400. + (now - ts).seconds
        if diff < 86400:
            good += 1
    return good

if __name__ == '__main__':
    good = check()
    msg = '%s good lapses' % (good, )
    if good > 30:
        print 'OK - %s' % (msg,)
        sys.exit(0)
    else:
        print 'CRITICAL - %s' % (msg,)
        sys.exit(2)
