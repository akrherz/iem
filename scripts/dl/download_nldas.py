"""Fetch the NLDAS forcing-a files for archiving
Run at 00 UTC and get the files from 4 days ago!
"""

import datetime
import urllib2
import subprocess
import tempfile
import os


def do(ts):
    """ Run for a given date! """
    for hr in range(24):
        now = ts.replace(hour=hr)

        uri = now.strftime("http://www.ftp.ncep.noaa.gov/data/nccf/com/nldas/"
                           "prod/nldas.%Y%m%d/nldas.t12z.force-a.grb2f"
                           ) + "%02i" % (hr, )

        try:
            req = urllib2.Request(uri)
            data = urllib2.urlopen(req, timeout=60).read()
        except:
            print 'NLDAS Download failed for: %s' % (uri,)
            continue
        tmpfn = tempfile.mktemp()
        o = open(tmpfn, 'w')
        o.write(data)
        o.close()

        cmd = ("/home/ldm/bin/pqinsert -p 'data a %s bogus "
               "model/nldas/nldas.t12z.force-a.grb2f%02i grib2' %s"
               ) % (now.strftime("%Y%m%d%H%M"), hr, tmpfn)
        subprocess.call(cmd, shell=True)

        os.remove(tmpfn)

if __name__ == '__main__':
    ts = datetime.datetime.utcnow() - datetime.timedelta(days=4)
    do(ts)
