"""Make an empty tree of RIDGE folders

Since we have web scrapers, we need to have empty folders to keep the Server
from having lots of 404s
"""
import os
import sys
import grp
from pyiem.network import Table as NetworkTable
import datetime

PRODS = {'NEXRAD': ['N0Q', 'N0S', 'N0U', 'N0Z', 'NET'],
         'TWDR': ['NET', 'TR0', 'TV0']}


def chgrp(filepath, gid):
    # https://gist.github.com/jmahmood/2505741
    uid = os.stat(filepath).st_uid
    os.chown(filepath, uid, gid)


def supermakedirs(path, mode, group):
    # http://stackoverflow.com/questions/5231901
    if not path or os.path.exists(path):
        return []
    (head, _) = os.path.split(path)
    res = supermakedirs(head, mode, group)
    os.mkdir(path)
    os.chmod(path, mode)
    chgrp(path, group)
    res += [path]
    return res


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
            supermakedirs(mydir, 0775, grp.getgrnam('ldm')[2])

if __name__ == '__main__':
    main(sys.argv)
