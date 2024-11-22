"""Send a tar file of our daily data to staging for upload to Google Drive!

Lets run at 12z for the previous date
"""

import os
import subprocess
from datetime import date, datetime, timedelta
from typing import Optional

import click
from pyiem.util import logger

LOG = logger()


def run(dt: date):
    """Upload this date's worth of data!"""
    os.chdir("/mesonet/tmp")
    tarfn = dt.strftime("iem_%Y%m%d.tgz")
    # Step 1: Create a gzipped tar file
    cmd = [
        "tar",
        "-czf",
        tarfn,
        f"/mesonet/ARCHIVE/data/{dt:%Y/%m/%d}",
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd, stderr=subprocess.PIPE)
    cmd = [
        "rsync",
        "-a",
        "--remove-source-files",
        "--rsync-path",
        f"mkdir -p /stage/IEMArchive/{dt:%Y/%m} && rsync",
        tarfn,
        f"mesonet@akrherz-desktop.agron.iastate.edu:"
        f"/stage/IEMArchive/{dt:%Y/%m}",
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), help="Specify a date to process"
)
@click.option("--year", type=int, help="Specify a year to process")
def main(dt: Optional[datetime], year: Optional[int]):
    """Go Main Go"""
    if year:
        now = date(year, 1, 1)
        ets = date(year + 1, 1, 1)
        while now < ets:
            run(now)
            now += timedelta(days=1)
    elif dt:
        run(dt.date())
    else:
        yesterday = date.today() - timedelta(days=1)
        run(yesterday)


if __name__ == "__main__":
    main()
