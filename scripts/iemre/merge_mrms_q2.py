"""Merge the 1km Q2 24 hour precip data estimates"""
import datetime
import sys
import os

import pytz
import numpy as np
from PIL import Image
import pyiem.mrms as mrms
from pyiem import iemre
from pyiem.util import ncopen


def findfile(ts):
    """See if we can find a file to use"""
    for hr in [0, -1, 1, -2, 2, -3, 3]:
        ts2 = ts + datetime.timedelta(hours=hr)
        fn = ts2.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/mrms/p24h_%Y%m%d%H00.png"
        )
        if os.path.isfile(fn):
            return fn


def run(ts):
    """Actually do the work, please"""
    nc = ncopen(iemre.get_daily_mrms_ncname(ts.year), "a", timeout=300)
    offset = iemre.daily_offset(ts)
    ncprecip = nc.variables["p01d"]
    ts += datetime.timedelta(hours=24)
    gmtts = ts.astimezone(pytz.utc)
    fn = findfile(gmtts)
    if fn is None:
        print(f"merge_mrms_q2 failed to find file for time: {gmtts}")
        return
    img = Image.open(fn)
    data = np.asarray(img)
    # data is 3500,7000 , starting at upper L
    data = np.flipud(data)
    # Anything over 254 is bad
    res = np.where(data > 254, 0, data)
    res = np.where(np.logical_and(data >= 0, data < 100), data * 0.25, res)
    res = np.where(
        np.logical_and(data >= 100, data < 180),
        25.0 + ((data - 100) * 1.25),
        res,
    )
    res = np.where(
        np.logical_and(data >= 180, data < 255),
        125.0 + ((data - 180) * 5.0),
        res,
    )

    y1 = int((iemre.NORTH - mrms.SOUTH) * 100.0)
    y0 = int((iemre.SOUTH - mrms.SOUTH) * 100.0)
    x0 = int((iemre.WEST - mrms.WEST) * 100.0)
    x1 = int((iemre.EAST - mrms.WEST) * 100.0)
    ncprecip[offset, :, :] = res[y0:y1, x0:x1]
    nc.close()


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        # 12 noon to prevent ugliness with timezones
        ts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]), 12, 0)
    else:
        ts = datetime.datetime.now() - datetime.timedelta(hours=24)
        ts = ts.replace(hour=12)

    ts = ts.replace(tzinfo=pytz.utc)
    ts = ts.astimezone(pytz.timezone("America/Chicago"))
    ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    run(ts)


if __name__ == "__main__":
    main(sys.argv)
