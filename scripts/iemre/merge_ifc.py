"""Merge the PNG IFC files into the daily netcdf file.

called from RUN_10_AFTER.sh
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
import numpy as np
from osgeo import gdal
from pyiem import iemre
from pyiem.util import archive_fetch, logger, ncopen, utc

gdal.UseExceptions()
LOG = logger()


def run(ts):
    """Process this date's worth of data"""
    LOG.info("Running for %s", ts)
    now = ts.replace(hour=0, minute=0)
    ets = now + timedelta(hours=24)
    interval = timedelta(minutes=5)
    currenttime = utc()

    total = None
    while now <= ets:
        gmt = now.astimezone(ZoneInfo("UTC"))
        if gmt > currenttime:
            break
        ppath = gmt.strftime("%Y/%m/%d/GIS/ifc/p05m_%Y%m%d%H%M.png")
        with archive_fetch(ppath) as fn:
            if fn is None:
                now += interval
                continue
            png = gdal.Open(fn, 0)
            data = png.ReadAsArray()  # units are mm per 5 minutes
            data = np.where(data > 254, 0, data) / 10.0
            if total is None:
                total = data
            else:
                total += data
        now += interval
    if total is None:
        LOG.info("No IFC Data found for date: %s", now)
        return

    ncfn = f"/mesonet/data/iemre/{ts.year}_ifc_daily.nc"
    idx = iemre.daily_offset(ts)
    with ncopen(ncfn, "a", timeout=300) as nc:
        nc.variables["p01d"][idx, :, :] = np.flipud(total)


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime):
    """Go Main Go"""
    # We are always running for a Central Timezone Date
    dt = dt.replace(tzinfo=ZoneInfo("America/Chicago"))
    run(dt)


if __name__ == "__main__":
    main()
