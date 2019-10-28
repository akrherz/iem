"""Download and archive the CFS data

Run from RUN_NOON.sh and we process the previous UTC day's data.

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


def dl(now, varname, scenario):
    """get the files"""
    s2 = "%02i" % (scenario,)
    uri = now.strftime(
        (
            "https://www.ftp.ncep.noaa.gov/data/nccf/com/cfs/prod/"
            "cfs/cfs.%Y%m%d/%H/time_grib_"
            + s2
            + "/"
            + varname
            + "."
            + s2
            + ".%Y%m%d%H.daily.grb2"
        )
    )
    response = exponential_backoff(requests.get, uri, timeout=60)
    if response is None or response.status_code != 200:
        print("download_cfs.py: dl %s failed" % (uri,))
        return
    tmpfn = "/tmp/%s.cfs.grib" % (varname,)
    fh = open(tmpfn, "wb")
    fh.write(response.content)
    fh.close()
    # Check out this file to see how much data we actually have, it had
    # better be a big number
    grb = pygrib.open(tmpfn)
    if grb.messages < REQUIRED_MSGS:
        print(
            ("download_cfs[%s] %s %s has only %s messages, need %s+")
            % (scenario, now, varname, grb.messages, REQUIRED_MSGS)
        )
    else:
        # Inject into LDM
        cmd = (
            "/home/ldm/bin/pqinsert -p 'data a %s blah "
            "model/cfs/%02i/%s.%s.%s.daily.grib2 grib' %s"
        ) % (
            now.strftime("%Y%m%d%H%M"),
            now.hour,
            varname,
            s2,
            now.strftime("%Y%m%d%H"),
            tmpfn,
        )
        subprocess.call(cmd, shell=True)

    os.remove(tmpfn)


def main():
    """Do main"""
    now = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    for hour in [0, 6, 12, 18]:
        now = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        for varname in ["tmax", "tmin", "prate", "dswsfc"]:
            # Control member 1 is the only one out 9 months
            dl(now, varname, 1)


if __name__ == "__main__":
    main()
