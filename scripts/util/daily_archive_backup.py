"""Send a tar file of our daily data to staging for upload to Google Drive!

Lets run at 12z for the previous date
"""

import datetime
import os
import subprocess
import sys

from pyiem.util import logger

LOG = logger()


def run(date):
    """Upload this date's worth of data!"""
    os.chdir("/mesonet/tmp")
    tarfn = date.strftime("iem_%Y%m%d.tgz")
    # Step 1: Create a gzipped tar file
    cmd = [
        "tar",
        "-czf",
        tarfn,
        f"/mesonet/ARCHIVE/data/{date:%Y}/{date:%m}/{date:%d}",
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd, stderr=subprocess.PIPE)
    cmd = date.strftime(
        f"rsync -a --remove-source-files "
        f"--rsync-path 'mkdir -p /stage/IEMArchive/%Y/%m && rsync' {tarfn} "
        "mesonet@metl60.agron.iastate.edu:/stage/IEMArchive/%Y/%m"
    )
    LOG.info(cmd)
    subprocess.call(cmd, shell=True)


def main(argv):
    """Go Main Go"""
    if len(argv) == 2:
        now = datetime.date(int(argv[1]), 1, 1)
        ets = datetime.date(int(argv[1]) + 1, 1, 1)
        while now < ets:
            run(now)
            now += datetime.timedelta(days=1)
    elif len(argv) == 4:
        now = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
        run(now)
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        run(yesterday)


if __name__ == "__main__":
    main(sys.argv)
