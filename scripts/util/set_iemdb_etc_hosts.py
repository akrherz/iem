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
    if sys.argv[1] == 'proxy':
        ip = '172.16.172.1'
        hads_ip = '172.16.170.1'
    data = open('/etc/hosts').read()
    result = []
    for line in data.split("\n"):
        if line.find("iemdb iemdb2") > 0:
            line = "%s iemdb iemdb2" % (ip, )
            print("Setting iemdb to ip: %s" % (ip, ))
        elif line.find("iemdb-hads") > 0:
            line = "%s iemdb-hads" % (hads_ip, )
            print("Setting iemdb-hads to ip: %s" % (hads_ip, ))
        elif line.find("iemdb-mos") > 0:
            line = "%s iemdb-mos" % (hads_ip, )
            print("Setting iemdb-mos to ip: %s" % (hads_ip, ))
        result.append(line)
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, '\n'.join(result))
    os.close(tmpfd)
    os.rename(tmpfn, '/etc/hosts')
    os.chmod('/etc/hosts', 0o644)


if __name__ == '__main__':
    main()
