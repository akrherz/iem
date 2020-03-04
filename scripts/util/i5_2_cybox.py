"""Move i5 analysis to staging for upload to Google Drive.

Run from RUN_MIDNIGHT.sh
"""
import os
import subprocess
import datetime
import glob
import sys

from pyiem.util import logger

LOG = logger()
REMOTEUSER = "mesonet@metl60.agron.iastate.edu"


def call(cmd):
    """Our custom caller."""
    LOG.debug(cmd)
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout = proc.stdout.read().decode("ascii", "ignore")
    stderr = proc.stderr.read().decode("ascii", "ignore")
    if stdout == "" and stderr == "":
        return
    LOG.info("cmd %s yielded stdout: %s stderr: %s", cmd, stdout, stderr)


def main(argv):
    """Go Main!"""
    if len(argv) == 4:
        date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        date = datetime.date.today() - datetime.timedelta(days=1)
    os.chdir("/mesonet/share/pickup/ntrans")

    basedir = date.strftime("%Y/%m/%d")
    for hour in range(24):
        remotedir = "/stage/NTRANS/wxarchive/%s/%02i" % (basedir, hour)
        cmd = "ssh %s mkdir -p %s" % (REMOTEUSER, remotedir)
        call(cmd)
        fns = glob.glob("wx_%s%02i*.zip" % (date.strftime("%Y%m%d"), hour))
        if not fns:
            LOG.info("wx date:%s hour:%s had no files?", date, hour)
            continue
        cmd = "rsync -a --remove-source-files %s %s:%s" % (
            " ".join(fns),
            REMOTEUSER,
            remotedir,
        )
        call(cmd)

    basedir = date.strftime("%Y/%m")
    remotedir = "/stage/NTRANS/wxarchive/forecast/%s" % (basedir,)
    cmd = "ssh %s mkdir -p %s" % (REMOTEUSER, remotedir)
    call(cmd)
    fns = glob.glob("fx_%s*.zip" % (date.strftime("%Y%m%d"),))
    if not fns:
        LOG.info("fx date:%s had no files?", date)
    else:
        cmd = "rsync -a --remove-source-files %s %s:%s" % (
            " ".join(fns),
            REMOTEUSER,
            remotedir,
        )
        call(cmd)


if __name__ == "__main__":
    main(sys.argv)
