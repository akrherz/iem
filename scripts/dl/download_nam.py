"""Get some soil grids from the NAM"""
import subprocess
import sys
import datetime
import os
import tempfile

import requests
import pygrib
from pyiem.util import exponential_backoff, logger

LOG = logger()


def need_to_run(valid, hr):
    """Check to see if we already have the radiation data we need"""
    gribfn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/nam/%H/"
        f"nam.t%Hz.conusnest.hiresf0{hr}.tm00.grib2"
    )
    if not os.path.isfile(gribfn):
        return True
    try:
        grbs = pygrib.open(gribfn)
        if grbs.messages < 5:
            LOG.debug("gribfn %s only has %s messages", gribfn, grbs.messages)
            return True
    except Exception:
        return True
    return False


def fetch(valid, hr):
    """Fetch the data for this timestamp"""
    uri = valid.strftime(
        "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nam/prod/"
        f"nam.%Y%m%d/nam.t%Hz.conusnest.hiresf0{hr}.tm00.grib2.idx"
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
        if tokens[3] in ["ULWRF", "DSWRF"]:
            if tokens[4] == "surface" and tokens[5].find("ave fcst") > 0:
                offsets.append([int(tokens[1])])
                neednext = True
        # Save soil temp and water at surface, 10cm and 40cm
        if tokens[3] in ["TSOIL", "SOILW"]:
            if tokens[4] in [
                "0-0.1 m below ground",
                "0.1-0.4 m below ground",
                "0.4-1 m below ground",
            ]:
                offsets.append([int(tokens[1])])
                neednext = True

    pqstr = valid.strftime(
        "data u %Y%m%d%H00 bogus model/nam/"
        f"%H/nam.t%Hz.conusnest.hiresf0{hr}.tm00.grib2 grib2"
    )

    if len(offsets) != 8:
        LOG.info("warning, found %s gribs for %s[%s]", len(offsets), valid, hr)
    for pr in offsets:
        headers = {"Range": "bytes=%s-%s" % (pr[0], pr[1])}
        req = exponential_backoff(
            requests.get, uri[:-4], headers=headers, timeout=30
        )
        if req is None:
            LOG.info("failure for uri: %s", uri)
            continue
        tmpfd = tempfile.NamedTemporaryFile(delete=False)
        tmpfd.write(req.content)
        tmpfd.close()
        subprocess.call(
            "pqinsert -p '%s' %s" % (pqstr, tmpfd.name), shell=True
        )
        os.unlink(tmpfd.name)


def main():
    """Go Main Go"""
    ts = datetime.datetime(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
    # script is called every hour, just short circuit the un-needed hours
    if ts.hour % 6 != 0:
        return
    times = [ts]
    times.append(ts - datetime.timedelta(hours=6))
    times.append(ts - datetime.timedelta(hours=24))
    for ts in times:
        for hr in range(6):
            if not need_to_run(ts, hr):
                continue
            LOG.debug("Running for ts: %s hr: %s", ts, hr)
            fetch(ts, hr)


if __name__ == "__main__":
    main()
