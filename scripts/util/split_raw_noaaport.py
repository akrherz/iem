"""Split archived noaaport files"""
from __future__ import print_function
import os
import datetime
import subprocess
from pyiem.nws.product import TextProduct


def main():
    """Go"""
    os.chdir("/mesonet/tmp")
    sts = datetime.datetime(2011, 7, 19)
    ets = datetime.datetime(2011, 8, 3)
    interval = datetime.timedelta(days=1)

    now = sts
    while now < ets:
        out = open('%s.data' % (now.strftime("%Y%m%d"),), 'w')
        subprocess.call(("tar -zxf /mesonet/ARCHIVE/raw/noaaport/%s/%s.tgz"
                         ) % (now.year, now.strftime("%Y%m%d")), shell=True)
        for q in range(0, 24):
            print("%s %s" % (now, q))
            fn = "%s%02i.txt" % (now.strftime("%Y%m%d"), q)
            if not os.path.isfile(fn):
                print('Missing %s' % (fn,))
                continue
            o = open(fn).read()
            prods = o.split("\003")
            for prod in prods:
                try:
                    p = TextProduct(prod)
                except Exception as exp:
                    continue
                if p.afos is not None and p.afos[:3] in ['HML', ]:
                    out.write(prod + "\003")
            os.unlink(fn)
        out.close()
        now += interval


if __name__ == '__main__':
    main()
