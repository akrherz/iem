"""Check the availability of NEXRAD Mosiacs.

called from RUN_0Z.sh
"""

import os
from datetime import datetime, timedelta, timezone

import click
from pyiem.util import archive_fetch, logger

LOG = logger()


def run(sts: datetime, ets: datetime):
    """Loop over a start to end time and look for missing N0Q products."""
    LOG.info("Checking N0Q availability from %s to %s", sts, ets)
    now = sts
    interval = timedelta(minutes=5)
    while now < ets:
        for comp in ["us", "ak", "hi", "pr", "gu"]:
            ppath = f"{now:%Y/%m/%d}/GIS/{comp}comp/n0q_{now:%Y%m%d%H%M}.png"
            with archive_fetch(ppath) as fn:
                if fn is None:
                    LOG.warning("[%s]%s is missing", comp, ppath)
                    continue
                if comp == "us" and os.stat(fn)[6] < 200000:
                    LOG.warning(
                        "%s too small, size: %s",
                        ppath,
                        os.stat(fn)[6],
                    )
        now += interval


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="UTC Date")
def main(dt: datetime):
    """Go Main Go"""
    sts = dt.replace(tzinfo=timezone.utc)
    ets = sts + timedelta(hours=24)
    run(sts, ets)


if __name__ == "__main__":
    main()
