"""Download the 5km FFG product.

Run from RUN_40_AFTER.sh
"""
from __future__ import print_function
import datetime
import subprocess
import tempfile
from ftplib import FTP, error_perm
import os


def do(ts):
    """ Run for a given date! """
    localfn = ts.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/ffg/5kmffg_%Y%d%m%H.grib2"
    )
    if os.path.isfile(localfn):
        return
    remotefn = ts.strftime("5kmffg_%Y%m%d%H.grb2")
    ftp = FTP('ftp.wpc.ncep.noaa.gov')
    ftp.login()
    ftp.cwd("workoff/ffg")
    tmpfn = tempfile.mktemp()
    fh = open(tmpfn, 'wb')
    errored = False
    try:
        ftp.retrbinary('RETR ' + remotefn, fh.write)
    except error_perm as err:
        print("download_ffg failed to fetch: %s %s" % (remotefn, err))
        errored = True
    ftp.close()
    fh.close()
    cmd = ("/home/ldm/bin/pqinsert -i -p 'data a %s bogus "
           "model/ffg/%s.grib2 grib2' %s"
           ) % (ts.strftime("%Y%m%d%H%M"), remotefn[:-5], tmpfn)
    if not errored:
        subprocess.call(cmd, shell=True)

    os.remove(tmpfn)


def main():
    """Go Main Go"""
    # Run for the last hour, when we are modulus 6
    ts = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    ts = ts.replace(minute=0)
    if ts.hour % 6 > 0:
        return
    for offset in [0, 24, 72]:
        do(ts - datetime.timedelta(hours=offset))


if __name__ == '__main__':
    main()
