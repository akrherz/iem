"""A util script used on daryl's laptop to switch 'iemdb' /etc/hosts entry

129.186.185.33 iemdb iemdb2
#127.0.0.1 iemdb iemdb2

"""
import sys
import tempfile
import os


def main():
    if len(sys.argv) == 1:
        print('Usage: python set_iemdb_etc_hosts.py <local|remote>')
        return
    ip = '127.0.0.1' if (sys.argv[1] == 'local') else '129.186.185.33'
    data = open('/etc/hosts').read()
    result = []
    for line in data.split("\n"):
        if line.find("iemdb iemdb2") > 0:
            line = "%s iemdb iemdb2" % (ip, )
            print("Setting iemdb to ip: %s" % (ip, ))
        result.append(line)
    (tmpfd, tmpfn) = tempfile.mkstemp()
    os.write(tmpfd, '\n'.join(result))
    os.close(tmpfd)
    os.rename(tmpfn, '/etc/hosts')


if __name__ == '__main__':
    main()
