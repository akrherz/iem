"""Download and archive the CFS data

Run from RUN_NOON.sh and 23z and we process the previous UTC day's data.

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


def check(now, varname, scenario) -> bool:
    """See what the IEM already has."""
    fn = (
        f"/mesonet/ARCHIVE/data/{now:%Y/%m/%d}/model/cfs/{now:%H}/"
        f"{varname}.{scenario:02d}.{now:%Y%m%d%H}.daily.grib2"
    )
    if not os.path.isfile(fn):
        return False
    grbs = pygrib.open(fn)
    messages = grbs.messages
    grbs.close()
    LOG.info("Found %s with %s messages", fn, messages)
    return messages > REQUIRED_MSGS


def dl(now, varname, scenario):
    """get the files"""
    s2 = f"{scenario:02d}"
    uri = (
        "https://nomads.ncep.noaa.gov/pub/data/nccf/com/cfs/prod/"
        f"cfs.{now:%Y%m%d/%H}/time_grib_{s2}/{varname}.{s2}"
        f".{now:%Y%m%d%H}.daily.grb2"
    )
    LOG.info("fetching %s", uri)
    response = exponential_backoff(requests.get, uri, timeout=60)
    if response is None or response.status_code != 200:
        LOG.warning("dl %s failed", uri)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        tmpfd.write(response.content)
    # Check out this file to see how much data we actually have, it had
    # better be a big number
    grb = pygrib.open(tmpfd.name)
    if grb.messages < REQUIRED_MSGS:
        LOG.warning(
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
            f"pqinsert -p 'data a {now:%Y%m%d%H%M} blah "
            f"model/cfs/{now:%H}/{varname}.{s2}.{now:%Y%m%d%H}.daily.grib2 "
            f"grib' {tmpfd.name}"
        )
        subprocess.call(cmd, shell=True)

    os.remove(tmpfd.name)


def main():
    """Do main"""
    # Run for yesterday and three days ago
    for offset in [1, 3]:
        now = utc() - datetime.timedelta(days=offset)
        for hour in [0, 6, 12, 18]:
            now = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            for varname in ["tmax", "tmin", "prate", "dswsfc"]:
                # Control member 1 is the only one out 9 months
                if not check(now, varname, 1):
                    dl(now, varname, 1)


if __name__ == "__main__":
    main()
