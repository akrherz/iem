"""Download and archive the CFS data

We'll do the 12 UTC run for yesterday run from RUN_2AM.sh

tmax
tmin
prate
dswsfc
"""
import datetime
import sys
import os
import subprocess
import requests
import pygrib
from pyiem.util import exponential_backoff


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
    o = open(tmpfn, 'wb')
    o.write(response.content)
    o.close()
    # Check out this file to see how much data we actually have, it had
    # better be a big number
    grb = pygrib.open(tmpfn)
    # 6 hourly data, we want at least 300 days?, so 4x300
    if grb.messages < 1200:
        print(("download_cfs %s %s has only %s messages, need 1200+"
               ) % (now, varname, grb.messages))
    else:
        # Inject into LDM
        cmd = ("/home/ldm/bin/pqinsert -p 'data a %s blah "
               "model/cfs/%02i/%s.01.%s.daily.grib2 grib' %s"
               ) % (now.strftime("%Y%m%d%H%M"), now.hour, varname,
                    now.strftime("%Y%m%d%H"), tmpfn)
        subprocess.call(cmd, shell=True)

    os.remove(tmpfn)


def main(argv):
    """Do main"""
    now = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    now = now.replace(hour=12, minute=0, second=0, microsecond=0)
    [dl(now, varname) for varname in ['tmax', 'tmin', 'prate', 'dswsfc']]

if __name__ == '__main__':
    main(sys.argv)
