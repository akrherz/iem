"""Split archived noaaport files"""
from __future__ import print_function
import os
import datetime
import subprocess

import pytz
import tqdm
from pyiem.nws.product import TextProduct


def main():
    """Go"""
    os.chdir("/mesonet/tmp/noaaport")
    sts = datetime.datetime(2017, 10, 10)
    sts = sts.replace(tzinfo=pytz.utc)
    ets = datetime.datetime(2017, 11, 3)
    ets = ets.replace(tzinfo=pytz.utc)
    interval = datetime.timedelta(days=1)

    now = sts
    while now < ets:
        subprocess.call(("tar -zxf /mesonet/ARCHIVE/raw/noaaport/%s/%s.tgz"
                         ) % (now.year, now.strftime("%Y%m%d")), shell=True)
        out = open("%s.txt" % (now.strftime("%Y%m%d"), ), 'w')
        for hour in tqdm.tqdm(range(0, 24), desc=now.strftime("%m%d")):
            fn = "%s%02i.txt" % (now.strftime("%Y%m%d"), hour)
            if not os.path.isfile(fn):
                print('Missing %s' % (fn,))
                continue
            fp = open(fn).read()
            prods = fp.split("\003")
            for prod in prods:
                if prod.find("RRSTAR") == -1:
                    continue
                try:
                    tp = TextProduct(prod, utcnow=now)
                except Exception as _exp:
                    continue
                if tp.afos == 'RRSTAR' and tp.source == 'KWOH':
                    out.write(prod + "\003")
            os.unlink(fn)
        out.close()
        now += interval


if __name__ == '__main__':
    main()
