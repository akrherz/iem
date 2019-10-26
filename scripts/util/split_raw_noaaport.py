"""Split archived noaaport files"""
from __future__ import print_function
import os
import datetime
import subprocess

import tqdm
from pyiem.util import utc
from pyiem.nws.product import TextProduct


def main():
    """Go"""
    os.chdir("/mesonet/tmp/noaaport")
    sts = utc(2018, 4, 24)
    ets = utc(2018, 6, 28)
    interval = datetime.timedelta(days=1)

    now = sts
    while now < ets:
        subprocess.call(
            ("tar -zxf /mesonet/ARCHIVE/raw/noaaport/%s/%s.tgz")
            % (now.year, now.strftime("%Y%m%d")),
            shell=True,
        )
        out = open("%s.txt" % (now.strftime("%Y%m%d"),), "w")
        for hour in tqdm.tqdm(range(0, 24), desc=now.strftime("%m%d")):
            fn = "%s%02i.txt" % (now.strftime("%Y%m%d"), hour)
            if not os.path.isfile(fn):
                print("Missing %s" % (fn,))
                continue
            # careful here to keep bad bytes from causing issues
            fp = open(fn, "rb").read()
            prods = fp.decode("utf-8", "ignore").split("\003")
            for prod in prods:
                if prod.find("RRSTAR") == -1:
                    continue
                try:
                    tp = TextProduct(prod, utcnow=now)
                except Exception:
                    continue
                if tp.afos == "RRSTAR":
                    out.write(prod + "\003")
            os.unlink(fn)
        out.close()
        now += interval


if __name__ == "__main__":
    main()
