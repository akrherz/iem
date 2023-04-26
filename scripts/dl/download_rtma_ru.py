"""
Download RTMA Rapid Updates grids

Run from RUN_50_AFTER.sh for previous hour
"""
import sys
import datetime
import os
import subprocess
import tempfile

import requests
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()


def fetch(dt):
    """Fetch the data for this timestamp"""
    localfn = (
        f"/mesonet/ARCHIVE/data/{dt:%Y/%m/%d}/model/rtma/{dt:%H}/"
        f"rtma2p5_ru.t{dt:%H%M}z.2dvaranl_ndfd.grb2"
    )
    if os.path.isfile(localfn):
        LOG.info("Skipping as we have data %s", localfn)
        return
    uri = (
        "https://nomads.weather.gov/pub/data/nccf/com/rtma/prod/"
        f"rtma2p5_ru.{dt:%Y%m%d}/rtma2p5_ru.t{dt:%H%M}z.2dvaranl_ndfd.grb2.idx"
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
        if tokens[3] in ["TMP", "DPT"]:
            offsets.append([int(tokens[1])])
            neednext = True

    if len(offsets) != 2:
        LOG.info("Failed to find required gribs")
        return

    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmpfp:
        for pr in offsets:
            headers = {"Range": f"bytes={pr[0]}-{pr[1]}"}
            req = exponential_backoff(
                requests.get, uri[:-4], headers=headers, timeout=30
            )
            if req is None:
                LOG.warning("failure for uri: %s", uri)
                continue
            tmpfp.write(req.content)
    cmd = [
        "pqinsert",
        "-i",
        "-p",
        (
            f"data a {dt:%Y%m%d%H%M} bogus model/rtma/"
            f"{dt:%H}/{localfn.split('/')[-1]} grib2"
        ),
        tmpfp.name,
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)
    os.unlink(tmpfp.name)


def main(argv):
    """Go Main Go"""
    if len(argv) == 5:
        ts = utc(*[int(s) for s in argv[1:5]])
    else:
        ts = utc() - datetime.timedelta(hours=1)

    # Backfilling mode
    for hroffset in [0, 6, 12, 24]:
        for minute in [0, 15, 30, 45]:
            valid = (ts - datetime.timedelta(hours=hroffset)).replace(
                minute=minute
            )
            fetch(valid)


if __name__ == "__main__":
    main(sys.argv)
