"""Send autolapse tar files to staging for archival.

Run from RUN_MIDNIGHT.sh for the previous date"""
import datetime
import subprocess
import os
import stat
import glob

from pyiem.util import logger

LOG = logger()


def main():
    """Run for the previous date, please"""
    valid = datetime.date.today() - datetime.timedelta(days=1)
    now = datetime.datetime.now()
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
        LOG.info("Found no files within the past day?")
        return

    remotepath = valid.strftime("/stage/iemwebcams/auto/%Y/%m/%d")
    cmd = (
        'rsync -a --rsync-path "mkdir -p %s && rsync" %s '
        "mesonet@metl60.agron.iastate.edu:%s"
    ) % (remotepath, " ".join(localfns), remotepath)
    LOG.debug(cmd)
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
