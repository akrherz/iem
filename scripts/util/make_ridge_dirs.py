"""Make an empty tree of RIDGE folders

Since we have web scrapers, we need to have empty folders to keep the Server
from having lots of 404s
"""
import os
import sys
from pyiem.network import Table as NetworkTable
import datetime

PRODS = {'NEXRAD': ['N0Q', 'N0S', 'N0U', 'N0Z', 'NET'],
         'TWDR': ['NET', 'TR0', 'TV0']}


def main(argv):
    """Go Main Go"""
    if len(argv) == 1:
        ts = datetime.datetime.utcnow()
    else:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]))
    nt = NetworkTable(['NEXRAD', 'TWDR'])
    basedir = ts.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge")
    for sid in nt.sts:
        for prod in PRODS[nt.sts[sid]['network']]:
            mydir = "%s/%s/%s" % (basedir, sid, prod)
            if os.path.isdir(mydir):
                continue
            os.makedirs(mydir, mode=0775)

if __name__ == '__main__':
    main(sys.argv)
