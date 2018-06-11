"""Process AWOS METAR file"""
from __future__ import print_function
import re
import os
import datetime
import ftplib
import subprocess

import pyiem.util as util

INCOMING = "/mesonet/data/incoming"


def fetch_files():
    """Fetch files """
    props = util.get_properties()

    fn = "%s/iaawos_metar.txt" % (INCOMING, )
    ftp = ftplib.FTP('165.206.203.34')
    ftp.login('rwis', props['rwis_ftp_password'])
    ftp.retrbinary('RETR METAR.txt', open(fn, 'wb').write)
    ftp.close()

    return fn


def main():
    """Go Main"""
    fn = fetch_files()
    utc = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    data = {}
    for line in open(fn):
        match = re.match("METAR K(?P<id>[A-Z1-9]{3})", line)
        if not match:
            continue
        gd = match.groupdict()
        data[gd['id']] = line

    fd = open('/tmp/awwwsosss', 'w')
    fd.write("\001\r\r\n")
    fd.write(("SAUS00 KISU %s\r\r\n"
              ) % (datetime.datetime.utcnow().strftime("%d%H%M"), ))
    fd.write("METAR\r\r\n")
    for sid in data:
        fd.write('%s=\r\r\n' % (data[sid].strip().replace("METAR ", ""), ))
    fd.write("\003")
    fd.close()
    proc = subprocess.Popen(("/home/ldm/bin/pqinsert -i -p 'data c %s "
                             "LOCDSMMETAR.dat LOCDSMMETAR.dat txt' %s"
                             ) % (utc, '/tmp/awwwsosss'), shell=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    os.waitpid(proc.pid, 0)


if __name__ == '__main__':
    main()
