"""Send autolapse tar files to staging for archival.

Run from RUN_MIDNIGHT.sh for the previous date"""

import glob
import os
import stat
import subprocess
from datetime import date, datetime, timedelta

from pyiem.util import logger

LOG = logger()


def main():
    """Run for the previous date, please"""
    valid = date.today() - timedelta(days=1)
    now = datetime.now()
    os.chdir("/mesonet/share/lapses/auto")
    localfns = []
    for tarfilename in glob.glob("*frames.tar"):
        # Make sure this file was generated yesterday and not old.
        mtime = os.stat(tarfilename)[stat.ST_MTIME]
        age = float(now.strftime("%s")) - mtime
        if age > 86400.0:
            continue
        localfns.append(tarfilename)
    if not localfns:
        LOG.warning("Found no files within the past day?")
        return

    remotepath = valid.strftime("/stage/iemwebcams/auto/%Y/%m/%d")
    cmd = [
        "rsync",
        "-a",
        "--rsync-path",
        f"mkdir -p {remotepath} && rsync",
        *localfns,
        f"mesonet@akrherz-desktop.agron.iastate.edu:{remotepath}",
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)


if __name__ == "__main__":
    main()
