"""Regenerate composites to fulfill various reasons.

Not called from anywhere, but often manually run :/
"""

import subprocess
from datetime import UTC, datetime, timedelta

import click
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--sts", required=True, help="Start Time", type=click.DateTime())
@click.option("--ets", required=True, help="End Time", type=click.DateTime())
def main(sts: datetime, ets: datetime):
    """Go Main Go"""
    sts = sts.replace(tzinfo=UTC)
    ets = ets.replace(tzinfo=UTC)
    interval = timedelta(minutes=5)
    now = sts
    while now < ets:
        cmd = [
            "python",
            "radar_composite.py",
            f"--valid={now:%Y-%m-%dT%H:%M}:00",
        ]
        LOG.info(" ".join(cmd))
        subprocess.call(cmd)
        now += interval


if __name__ == "__main__":
    main()
