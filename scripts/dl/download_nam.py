"""Get some soil grids from the NAM.

Run from RUN_40_AFTER.sh for a UTC timestamp 3 hours ago.
"""

import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import click
import httpx
import pygrib
from pyiem.util import archive_fetch, exponential_backoff, logger

LOG = logger()


def need_to_run(valid: datetime, hr) -> bool:
    """Check to see if we already have the radiation data we need"""
    ppath = valid.strftime(
        f"%Y/%m/%d/model/nam/%H/nam.t%Hz.conusnest.hiresf0{hr}.tm00.grib2"
    )
    with archive_fetch(ppath) as fn:
        if fn is None:
            return True
        try:
            with pygrib.open(fn) as grbs:
                if grbs.messages < 5:
                    LOG.info(
                        "gribfn %s has %s/5 messages", ppath, grbs.messages
                    )
                    return True
        except Exception as exp:
            LOG.exception(exp)
            return True
    return False


def fetch(valid, hr):
    """Fetch the data for this timestamp"""
    uri = valid.strftime(
        "https://noaa-nam-pds.s3.amazonaws.com/"
        f"nam.%Y%m%d/nam.t%Hz.conusnest.hiresf0{hr}.tm00.grib2.idx"
    )
    req = exponential_backoff(httpx.get, uri, timeout=30)
    if req is None or req.status_code != 200:
        LOG.warning("failed to get idx: %s", uri)
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
            tokens[3] in ["ULWRF", "DSWRF"]
            and tokens[4] == "surface"
            and tokens[5].find("ave fcst") > 0
        ):
            offsets.append([int(tokens[1])])
            neednext = True
        # Save soil temp and water at surface, 10cm and 40cm
        if tokens[3] in ["TSOIL", "SOILW"] and tokens[4] in [
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
        headers = {"Range": f"bytes={pr[0]}-{pr[1]}"}
        req = exponential_backoff(
            httpx.get, uri[:-4], headers=headers, timeout=30
        )
        if req is None:
            LOG.info("failure for uri: %s", uri)
            continue
        with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
            tmpfd.write(req.content)
        subprocess.call(["pqinsert", "-p", pqstr, tmpfd.name])
        os.unlink(tmpfd.name)


@click.command()
@click.option("--valid", required=True, type=click.DateTime(), help="UTC Time")
def main(valid: datetime):
    """Go Main Go"""
    ts = valid.replace(tzinfo=timezone.utc)
    # script is called every hour, just short circuit the un-needed hours
    if ts.hour % 6 != 0:
        LOG.info("Aborting as time %s is not modulo 6", ts)
        return
    times = [
        ts,
        ts - timedelta(hours=6),
        ts - timedelta(hours=24),
    ]
    for ts in times:
        for hr in range(6):
            if not need_to_run(ts, hr):
                continue
            LOG.info("Running for ts: %s hr: %s", ts, hr)
            fetch(ts, hr)


if __name__ == "__main__":
    main()
