"""Copies the appropriate MRMS 24 HR raster for a calendar date.

Run from RUN_MIDNIGHT.sh
"""

import subprocess
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
from pyiem.util import archive_fetch, logger

LOG = logger()


def workflow(dt):
    """Copy things around."""
    basefn = dt.strftime("%Y/%m/%d/GIS/mrms/p24h_%Y%m%d%H00")
    yest = dt - timedelta(days=1)
    for suffix in ["png", "wld"]:
        ppath = f"{basefn}.{suffix}"
        with archive_fetch(ppath) as target:
            if target is None:
                LOG.warning("ERROR: %s not found", target)
                return
            cmd = [
                "pqinsert",
                "-i",
                "-p",
                f"gis a {yest:%Y%m%d%H%M} "
                f"GIS/mrms_calday_{yest:%Y%m%d}.{suffix} "
                f"GIS/mrms_calday_{yest:%Y%m%d}.{suffix} {suffix}",
                target,
            ]
            subprocess.call(cmd)
            LOG.info("%s -> %s", target, " ".join(cmd))


@click.command()
@click.option(
    "--date",
    "dt",
    required=True,
    help="Date to process",
    type=click.DateTime(),
)
def main(dt: datetime):
    """Do Something"""
    # Compute midnight Central as UTC
    dt = dt.replace(tzinfo=ZoneInfo("America/Chicago")).astimezone(
        ZoneInfo("UTC")
    )
    LOG.info("Computed midnight UTC of %s", dt)
    workflow(dt)


if __name__ == "__main__":
    # Go Main Go
    main()
