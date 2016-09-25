import os
import datetime
import subprocess
from pyiem.nws.product import TextProduct

os.chdir("/mesonet/tmp")
sts = datetime.datetime(2011, 7, 19)
ets = datetime.datetime(2011, 8, 3)
interval = datetime.timedelta(days=1)

now = sts
while now < ets:
    out = open('%s.data' % (now.strftime("%Y%m%d"),), 'w')
    subprocess.call(("tar -zxf /mesonet/ARCHIVE/raw/noaaport/%s.tgz"
                     ) % (now.strftime("%Y%m%d"),))
    for q in range(0, 24):
        print now, q
        fn = "%s%02i.txt" % (now.strftime("%d"), q)
        if not os.path.isfile(fn):
            print 'Missing', fn
            continue
        o = open(fn).read()
        prods = o.split("\003")
        for prod in prods:
            try:
                p = TextProduct(prod)
            except:
                continue
            if p.afos is not None and p.afos[:3] in ['HML', ]:
                out.write(prod + "\003")
        os.unlink("%s%02i.txt" % (now.strftime("%d"), q))
    out.close()
    now += interval
