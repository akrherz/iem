"""Send a tar file of our daily data to CyBox!

Note, needs a ~/.netrc file with 600 perms

Lets run at 12z for the previous date
"""
import datetime
import subprocess
import os
import sys

from pyiem.ftpsession import send2box


def run(date):
    """Upload this date's worth of data!"""
    os.chdir("/mesonet/tmp")
    tarfn = date.strftime("iem_%Y%m%d.tgz")
    # Step 1: Create a gzipped tar file
    cmd = "tar -czf %s /mesonet/ARCHIVE/data/%s" % (
        tarfn,
        date.strftime("%Y/%m/%d"),
    )
    subprocess.call(cmd, shell=True, stderr=subprocess.PIPE)
    send2box(tarfn, date.strftime("/IEMArchive/%Y/%m"), tmpdir="/mesonet/tmp")
    os.unlink(tarfn)


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
