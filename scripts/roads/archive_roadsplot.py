"""Archive a road conditions plot every 5 minutes.

Called from RUN_5MIN.sh
"""

import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import click
import httpx
from pyiem.util import archive_fetch, logger, utc

LOG = logger()


def do(now: datetime):
    """Run for a given timestamp."""
    ppath = now.strftime("%Y/%m/%d/iaroads/iaroads_%H%M.png")
    with archive_fetch(ppath) as fn:
        if fn is not None:
            LOG.info("skipping as file %s exists", ppath)
            return
    LOG.info("running for %s", now)

    # CAREFUL, web takes valid in CST/CDT
    service = now.astimezone(ZoneInfo("America/Chicago")).strftime(
        "http://iem.local/roads/iem.php?valid=%Y-%m-%d%%20%H:%M"
    )
    routes = "ac" if (utc() - now) < timedelta(minutes=10) else "a"
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


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
def main(valid: datetime):
    """Go Main Go"""
    valid = valid.replace(tzinfo=timezone.utc)
    for offset in [0, 1440, 1440 + 720]:
        do(valid - timedelta(minutes=offset))


if __name__ == "__main__":
    main()
