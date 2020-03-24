"""Regenerate composites to fulfill various reasons."""
import datetime
import sys
import subprocess

from pyiem.util import logger, utc

LOG = logger()


def main(argv):
    """Go Main Go"""
    sts = utc(
        int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5])
    )
    ets = utc(
        int(argv[6]), int(argv[7]), int(argv[8]), int(argv[9]), int(argv[10])
    )
    interval = datetime.timedelta(minutes=5)
    now = sts
    while now < ets:
        cmd = now.strftime("python radar_composite.py %Y %m %d %H %M")
        LOG.debug(cmd)
        subprocess.call(cmd, shell=True)
        now += interval


if __name__ == "__main__":
    main(sys.argv)
