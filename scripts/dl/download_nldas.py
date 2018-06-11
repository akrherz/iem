"""Fetch the NLDAS forcing-a files for archiving
Run at 00 UTC and get the files from 4 days ago!
"""
from __future__ import print_function
import datetime
import subprocess
import tempfile
import os

import requests


def do(ts):
    """ Run for a given date! """
    for hr in range(24):
        now = ts.replace(hour=hr)

        uri = now.strftime("http://www.ftp.ncep.noaa.gov/data/nccf/com/nldas/"
                           "prod/nldas.%Y%m%d/nldas.t12z.force-a.grb2f"
                           ) + "%02i" % (hr, )

        try:
            req = requests.get(uri, timeout=60)
            if req.status_code != 200:
                raise Exception("status code is %s" % (req.status_code, ))
        except Exception as _exp:
            print('NLDAS Download failed for: %s' % (uri,))
            continue
        tmpfn = tempfile.mktemp()
        fh = open(tmpfn, 'wb')
        fh.write(req.content)
        fh.close()

        cmd = ("/home/ldm/bin/pqinsert -p 'data a %s bogus "
               "model/nldas/nldas.t12z.force-a.grb2f%02i grib2' %s"
               ) % (now.strftime("%Y%m%d%H%M"), hr, tmpfn)
        subprocess.call(cmd, shell=True)

        os.remove(tmpfn)


def main():
    """Go Main Go"""
    ts = datetime.datetime.utcnow() - datetime.timedelta(days=5)
    do(ts)


if __name__ == '__main__':
    main()
