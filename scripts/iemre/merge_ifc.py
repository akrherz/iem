"""Merge the PNG IFC files into the daily netcdf file"""
import datetime
import os
import sys
from zoneinfo import ZoneInfo

import numpy as np
from osgeo import gdal
from pyiem import iemre
from pyiem.util import logger, ncopen, utc

LOG = logger()


def run(ts):
    """Process this date's worth of data"""
    now = ts.replace(hour=0, minute=0)
    ets = now + datetime.timedelta(hours=24)
    interval = datetime.timedelta(minutes=5)
    currenttime = utc()

    total = None
    while now <= ets:
        gmt = now.astimezone(ZoneInfo("UTC"))
        if gmt > currenttime:
            break
        fn = gmt.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ifc/p05m_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fn):
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


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        date = datetime.datetime(
            int(argv[1]), int(argv[2]), int(argv[3]), 12, 0
        )
    else:
        date = datetime.datetime.now()
        date = date - datetime.timedelta(minutes=60)
        date = date.replace(hour=12, minute=0, second=0, microsecond=0)
    # Stupid pytz timezone dance
    date = date.replace(tzinfo=ZoneInfo("UTC"))
    date = date.astimezone(ZoneInfo("America/Chicago"))
    run(date)


if __name__ == "__main__":
    main(sys.argv)
