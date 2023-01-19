"""Get grids from the GFS that we care about.

At 2GB per run, we don't have capacity to archive this all.  So we save 1-2
days worth of data into /mesonet/tmp/gfs/

RUN from RUN_20_AFTER.sh
"""
import sys
import datetime
import os

import requests
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()
BASEDIR = "/mesonet/tmp/gfs"


def cull(valid):
    """Cull old content."""
    mydir = os.path.join(BASEDIR, valid.strftime("%Y%m%d%H"))
    if os.path.isdir(mydir):
        for fn in os.listdir(mydir):
            os.unlink(os.path.join(mydir, fn))
        # now remove the directory as well
        os.rmdir(mydir)


def need_to_run(valid, hr):
    """Check for a need to run for this forecast."""
    mydir = os.path.join(BASEDIR, valid.strftime("%Y%m%d%H"))
    if not os.path.isdir(mydir):
        os.makedirs(mydir, exist_ok=True)
    gribfn = valid.strftime(f"{mydir}/gfs.t%Hz.sfluxgrbf{hr:03.0f}.grib2")
    return not os.path.isfile(gribfn)


def fetch(valid, hr):
    """Fetch the data for this timestamp"""
    uri = valid.strftime(
        "https://ftpprd.ncep.noaa.gov/data/nccf/com/gfs/prod/"
        f"gfs.%Y%m%d/%H/atmos/gfs.t%Hz.sfluxgrbf{hr:03.0f}.grib2.idx"
    )
    req = exponential_backoff(requests.get, uri, timeout=30)
    if req is None or req.status_code != 200:
        LOG.info("failed to get idx: %s", uri)
        return

    offsets = []
    neednext = False
    for line in req.content.decode("utf-8").split("\n"):
        tokens = line.split(":")
        if len(tokens) < 3:
            continue
        if neednext:
            offsets[-1].append(int(tokens[1]))
            neednext = False
        # Precip and high/low temp
        if tokens[3] in ["PRATE", "TMAX", "TMIN"]:
            offsets.append([int(tokens[1])])
            neednext = True
        elif tokens[3] in ["ULWRF", "DSWRF"]:
            if tokens[4] == "surface" and tokens[5].find("ave fcst") > 0:
                offsets.append([int(tokens[1])])
                neednext = True
        # Save soil temp and water at surface, 10cm and 40cm
        elif tokens[3] in ["TSOIL", "SOILW"]:
            if tokens[4] in [
                "0-0.1 m below ground",
                "0.1-0.4 m below ground",
                "0.4-1 m below ground",
                "1-2 m below ground",
            ]:
                offsets.append([int(tokens[1])])
                neednext = True

    fn = valid.strftime(
        f"{BASEDIR}/%Y%m%d%H/gfs.t%Hz.sfluxgrbf{hr:03.0f}.grib2"
    )
    LOG.info("writing %s", fn)
    if len(offsets) != 13 and hr > 0:
        LOG.warning("found %s gribs for %s[%s]", len(offsets), valid, hr)
    for pr in offsets:
        headers = {"Range": f"bytes={pr[0]}-{pr[1]}"}
        req = exponential_backoff(
            requests.get, uri[:-4], headers=headers, timeout=30
        )
        if req is None:
            LOG.warning("failure for uri: %s", uri)
            continue
        with open(fn, "ab") as fh:
            fh.write(req.content)


def main(argv):
    """Go Main Go"""
    ts = utc(*[int(s) for s in argv[1:5]])
    # script is called every hour, just short circuit the un-needed hours
    if ts.hour % 6 != 0:
        return
    times = [ts, ts - datetime.timedelta(hours=6)]
    for ts in times:
        for hr in range(0, 385, 6):
            if need_to_run(ts, hr):
                fetch(ts, hr)
    # now cull old content
    for hr in range(72, 97, 6):
        cull(ts - datetime.timedelta(hours=hr))


if __name__ == "__main__":
    main(sys.argv)
