"""Regenerate composites to fulfill various reasons."""
import datetime
import sys
import subprocess

from pyiem.util import logger, utc

LOG = logger()


def main(argv):
    """Go Main Go"""
    sts = utc(*[int(x) for x in argv[1:6]])
    ets = utc(*[int(x) for x in argv[6:11]])
    interval = datetime.timedelta(minutes=5)
    now = sts
    while now < ets:
        cmd = f"python radar_composite.py {now:%Y %m %d %H %M}"
        LOG.debug(cmd)
        subprocess.call(cmd, shell=True)
        now += interval


if __name__ == "__main__":
    main(sys.argv)
