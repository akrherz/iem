"""Download and archive the CFS data

We'll do the 12 UTC run for yesterday run from RUN_2AM.sh

tmax
tmin
prate
dswsfc
"""
from __future__ import print_function
import datetime
import os
import subprocess

import requests
import pygrib
from pyiem.util import exponential_backoff

# Should have at least 9 months of data, so roughtly
REQUIRED_MSGS = 9 * 30 * 4


def dl(now, varname):
    """get the files"""
    uri = now.strftime(("http://www.ftp.ncep.noaa.gov/data/nccf/com/cfs/prod/"
                        "cfs/cfs.%Y%m%d/%H/time_grib_01/" +
                        varname + ".01.%Y%m%d%H.daily.grb2"))
    response = exponential_backoff(requests.get, uri, timeout=60)
    if response is None or response.status_code != 200:
        print('download_cfs.py: dl %s failed' % (uri,))
        return
    tmpfn = "/tmp/%s.cfs.grib" % (varname, )
    fh = open(tmpfn, 'wb')
    fh.write(response.content)
    fh.close()
    # Check out this file to see how much data we actually have, it had
    # better be a big number
    grb = pygrib.open(tmpfn)
    if grb.messages < REQUIRED_MSGS:
        print(("download_cfs %s %s has only %s messages, need %s+"
               ) % (now, varname, grb.messages, REQUIRED_MSGS))
    else:
        # Inject into LDM
        cmd = ("/home/ldm/bin/pqinsert -p 'data a %s blah "
               "model/cfs/%02i/%s.01.%s.daily.grib2 grib' %s"
               ) % (now.strftime("%Y%m%d%H%M"), now.hour, varname,
                    now.strftime("%Y%m%d%H"), tmpfn)
        subprocess.call(cmd, shell=True)

    os.remove(tmpfn)


def main():
    """Do main"""
    now = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    now = now.replace(hour=12, minute=0, second=0, microsecond=0)
    for varname in ['tmax', 'tmin', 'prate', 'dswsfc']:
        dl(now, varname)


if __name__ == '__main__':
    main()
