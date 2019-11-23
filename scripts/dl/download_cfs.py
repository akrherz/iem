"""Download and archive the CFS data

Run from RUN_NOON.sh and we process the previous UTC day's data.

tmax
tmin
prate
dswsfc
"""
import datetime
import os
import subprocess
import tempfile

import requests
import pygrib
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()
# Should have at least 9 months of data, so roughtly
REQUIRED_MSGS = 9 * 30 * 4


def dl(now, varname, scenario):
    """get the files"""
    s2 = "%02i" % (scenario,)
    uri = now.strftime(
        (
            "https://ftpprd.ncep.noaa.gov/data/nccf/com/cfs/prod/"
            "cfs/cfs.%Y%m%d/%H/time_grib_"
            + s2
            + "/"
            + varname
            + "."
            + s2
            + ".%Y%m%d%H.daily.grb2"
        )
    )
    LOG.debug("fetching %s", uri)
    response = exponential_backoff(requests.get, uri, timeout=60)
    if response is None or response.status_code != 200:
        LOG.info("dl %s failed", uri)
        return
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    tmpfd.write(response.content)
    tmpfd.close()
    # Check out this file to see how much data we actually have, it had
    # better be a big number
    grb = pygrib.open(tmpfd.name)
    if grb.messages < REQUIRED_MSGS:
        LOG.info(
            "[%s] %s %s has only %s messages, need %s+",
            scenario,
            now,
            varname,
            grb.messages,
            REQUIRED_MSGS,
        )
    else:
        # Inject into LDM
        cmd = (
            "pqinsert -p 'data a %s blah "
            "model/cfs/%02i/%s.%s.%s.daily.grib2 grib' %s"
        ) % (
            now.strftime("%Y%m%d%H%M"),
            now.hour,
            varname,
            s2,
            now.strftime("%Y%m%d%H"),
            tmpfd.name,
        )
        subprocess.call(cmd, shell=True)

    os.remove(tmpfd.name)


def main():
    """Do main"""
    now = utc() - datetime.timedelta(days=1)
    for hour in [0, 6, 12, 18]:
        now = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        for varname in ["tmax", "tmin", "prate", "dswsfc"]:
            # Control member 1 is the only one out 9 months
            dl(now, varname, 1)


if __name__ == "__main__":
    main()
