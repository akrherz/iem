"""A util script used on daryl's laptop to switch 'iemdb' /etc/hosts entry

129.186.185.33 iemdb iemdb2
#127.0.0.1 iemdb iemdb2

"""
from __future__ import print_function
import sys
import tempfile
import os

METVM4, METVM5, METVM6 = range(3)
IPS = ['172.16.170.1', '172.16.171.1', '172.16.172.1']
LOOKUP = {
    "": IPS[METVM6],
    "-hads": IPS[METVM4],
    "-iemre": IPS[METVM4],
    "-mos": IPS[METVM5],
    "-nldn": IPS[METVM5],
    "-radar": IPS[METVM5],
    "-smos": IPS[METVM5],
    "-talltowers": IPS[METVM5],
}


def main(argv):
    """Go Main Go"""
    if len(argv) == 1:
        print('Usage: python set_iemdb_etc_hosts.py <local|proxy>')
        return
    data = open('/etc/hosts').read()
    result = []
    for line in data.split("\n"):
        result.append(line)
        if line.startswith('# ---AUTOGEN---'):
            print("Found ---AUTOGEN---")
            break
    for dbname in LOOKUP:
        ip = LOOKUP[dbname] if argv[1] == 'proxy' else '127.0.0.1'
        print("%s -> %s" % (dbname, ip))
        result.append("%s iemdb%s.local" % (ip, dbname))
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, ('\n'.join(result)).encode('ascii'))
    os.write(tmpfd, b'\n')
    os.close(tmpfd)
    os.rename(tmpfn, '/etc/hosts')
    os.chmod('/etc/hosts', 0o644)


if __name__ == '__main__':
    main(sys.argv)
