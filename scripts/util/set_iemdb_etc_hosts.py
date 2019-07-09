"""A util script used on daryl's laptop to switch 'iemdb' /etc/hosts entry

129.186.185.33 iemdb iemdb2
#127.0.0.1 iemdb iemdb2

"""
from __future__ import print_function
import sys
import tempfile
import os


def main():
    """Go Main Go"""
    if len(sys.argv) == 1:
        print('Usage: python set_iemdb_etc_hosts.py <local|proxy>')
        return
    ip = '127.0.0.1'
    hads_ip = '127.0.0.1'
    iemre_ip = '127.0.0.1'
    if sys.argv[1] == 'proxy':
        ip = '172.16.172.1'
        hads_ip = '172.16.170.1'
        iemre_ip = '172.16.173.1'
    data = open('/etc/hosts').read()
    result = []
    for line in data.split("\n"):
        if line.find("iemdb.local iemdb2.local") > 0:
            line = "%s iemdb.local iemdb2.local" % (ip, )
            print("Setting iemdb.local to ip: %s" % (ip, ))
        elif line.find("iemdb-hads.local") > 0:
            line = "%s iemdb-hads.local" % (hads_ip, )
            print("Setting iemdb-hads.local to ip: %s" % (hads_ip, ))
        elif line.find("iemdb-mos.local") > 0:
            line = "%s iemdb-mos.local" % (hads_ip, )
            print("Setting iemdb-mos.local to ip: %s" % (hads_ip, ))
        elif line.find("iemdb-iemre.local") > 0:
            line = "%s iemdb-iemre.local" % (iemre_ip, )
            print("Setting iemdb-iemre.local to ip: %s" % (iemre_ip, ))
        result.append(line)
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, '\n'.join(result))
    os.close(tmpfd)
    os.rename(tmpfn, '/etc/hosts')
    os.chmod('/etc/hosts', 0o644)


if __name__ == '__main__':
    main()
