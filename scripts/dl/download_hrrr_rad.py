"""
 Since the NOAAPort feed of HRRR data does not have radiation, we should
 download this manually from NCEP

Run at 40 AFTER for the previous hour

"""
import datetime
import os
import subprocess
import sys
import tempfile

import requests
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()


def need_to_run(valid):
    """Check to see if we already have the radiation data we need"""
    gribfn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/"
        "%H/hrrr.t%Hz.3kmf01.grib2"
    )
    return not os.path.isfile(gribfn)


def fetch(valid):
    """Fetch the radiation data for this timestamp
    22:23684154:d=2023041000:DSWRF:surface:0-15 min ave fcst:
    """
    uri = valid.strftime(
        (
            "https://nomads.ncep.noaa.gov/pub/data/nccf/"
            "com/hrrr/prod/hrrr.%Y%m%d/conus/hrrr.t%Hz."
            "wrfsubhf01.grib2.idx"
        )
    )
    req = exponential_backoff(requests.get, uri, timeout=30)
    if req is None or req.status_code != 200:
        LOG.warning("failed to get idx %s", uri)
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
        if (
            tokens[3]
            in [
                "DSWRF",
            ]
            and tokens[5].find("ave fcst") > -1
        ):
            offsets.append([int(tokens[1])])
            neednext = True
    pqstr = valid.strftime(
        "data u %Y%m%d%H00 bogus model/hrrr/%H/hrrr.t%Hz.3kmf01.grib2 grib2"
    )

    if len(offsets) != 4:
        LOG.warning("warning, found %s gribs for %s", len(offsets), valid)
    for pr in offsets:
        headers = {"Range": f"bytes={pr[0]}-{pr[1]}"}
        req = exponential_backoff(
            requests.get, uri[:-4], headers=headers, timeout=30
        )
        if req is None:
            LOG.info("failure for uri: %s", uri)
            continue
        with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
            tmpfd.write(req.content)
        subprocess.call(["pqinsert", "-p", pqstr, tmpfd.name])
        os.unlink(tmpfd.name)


def main(argv):
    """Go Main Go"""
    times = []
    if len(argv) == 5:
        times.append(utc(*[int(i) for i in argv[1:]]))
    else:
        times.append(utc() - datetime.timedelta(hours=1))
        times.append(utc() - datetime.timedelta(hours=6))
        times.append(utc() - datetime.timedelta(hours=24))
    for ts in times:
        if not need_to_run(ts):
            continue
        LOG.info("running for %s", ts)
        fetch(ts)


if __name__ == "__main__":
    main(sys.argv)
