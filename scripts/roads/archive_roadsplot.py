"""Archive a road conditions plot every 5 minutes.

Called from RUN_5MIN.sh
"""

import datetime
import os
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

import httpx
from pyiem.util import logger, utc

LOG = logger()


def do(now):
    """Run for a given timestamp."""
    fn = now.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/iaroads/iaroads_%H%M.png"
    )
    if os.path.isfile(fn):
        LOG.info("skipping as file %s exists", fn)
        return
    LOG.info("running for %s", now)

    # CAREFUL, web takes valid in CST/CDT
    service = now.astimezone(ZoneInfo("America/Chicago")).strftime(
        "http://iem.local/roads/iem.php?valid=%Y-%m-%d%%20%H:%M"
    )
    routes = "ac" if (utc() - now) < datetime.timedelta(minutes=10) else "a"
    if routes == "ac":
        service = "http://iem.local/roads/iem.php"

    req = httpx.get(service, timeout=60)
    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        tmpfd.write(req.content)
    pqstr = (
        f"plot {routes} {now:%Y%m%d%H%M} iaroads.png "
        f"iaroads/iaroads_{now:%H%M}.png png"
    )
    LOG.info(pqstr)
    subprocess.call(["pqinsert", "-i", "-p", pqstr, tmpfd.name])
    os.unlink(tmpfd.name)


def main(argv):
    """Go Main Go"""
    now = utc(*[int(i) for i in argv[1:6]])
    for offset in [0, 1440, 1440 + 720]:
        valid = now - datetime.timedelta(minutes=offset)
        do(valid)


if __name__ == "__main__":
    main(sys.argv)
