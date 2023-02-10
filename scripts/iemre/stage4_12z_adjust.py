"""Use the QC'd 12z 24 Hour files to adjust hourly data."""
import sys
import os
import datetime

import numpy as np
from scipy.interpolate import NearestNDInterpolator
import pygrib
from pyiem import iemre
from pyiem.util import ncopen, logger, utc

LOG = logger()


def save12z(ts, val):
    """Save the data to our daily 12z file."""
    ncfn = f"/mesonet/data/stage4/{ts.year}_stage4_daily.nc"
    if not os.path.isfile(ncfn):
        LOG.warning("File not found! %s", ncfn)
        return
    idx = iemre.daily_offset(ts)
    LOG.debug("Writing 12z grid to %s at idx: %s", ncfn, idx)
    with ncopen(ncfn, "a") as nc:
        # Account for pre-2002 shape difference
        if val.shape == (880, 1160):
            nc.variables["p01d_12z"][idx, 1:, :] = val[:, 39:]
        else:
            nc.variables["p01d_12z"][idx] = val


def merge(ts):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """

    # Load up the 12z 24h total, this is what we base our deltas on
    fn = (
        "/mesonet/ARCHIVE/data/"
        f"{ts:%Y/%m/%d}/stage4/ST4.{ts:%Y%m%d%H}.24h.grib"
    )
    if not os.path.isfile(fn):
        LOG.info("stage4_12z_adjust %s is missing", fn)
        return False

    grbs = pygrib.open(fn)
    grb = grbs[1]
    val = grb.values
    save12z(ts, val)
    lats, lons = grb.latlons()
    # can save a bit of memory as we don't need all data
    stride = slice(None, None, 3)
    lats = np.ravel(lats[stride, stride])
    lons = np.ravel(lons[stride, stride])
    vals = np.ravel(val[stride, stride])
    # Clip large values
    vals = np.where(vals > 250.0, 0, vals)
    nn = NearestNDInterpolator((lons, lats), vals)
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    stage4 = nn(xi, yi)
    # Prevent Large numbers, negative numbers
    stage4 = np.where(stage4 < 10000.0, stage4, 0.0)
    stage4 = np.where(stage4 < 0.0, 0.0, stage4)

    ts0 = ts - datetime.timedelta(days=1)
    offset0 = iemre.hourly_offset(ts0)
    offset1 = iemre.hourly_offset(ts)
    # Running at 12 UTC 1 Jan
    if offset0 > offset1:
        offset0 = 0
    # Open up our RE file
    with ncopen(iemre.get_hourly_ncname(ts.year), "a", timeout=300) as nc:
        iemre_total = np.sum(
            nc.variables["p01m"][offset0:offset1, :, :], axis=0
        )
        iemre_total = np.where(iemre_total > 0.0, iemre_total, 0.00024)
        iemre_total = np.where(iemre_total < 10000.0, iemre_total, 0.00024)
        multiplier = stage4 / iemre_total
        for offset in range(offset0, offset1):
            # Get the unmasked dadta
            data = nc.variables["p01m"][offset, :, :]

            # Keep data within reason
            data = np.where(data > 10000.0, 0.0, data)
            # 0.00024 / 24
            adjust = np.where(data > 0, data, 0.00001) * multiplier
            adjust = np.where(adjust > 250.0, 0, adjust)
            nc.variables["p01m"][offset, :, :] = np.where(
                adjust < 0.01, 0, adjust
            )


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        ts = utc(int(argv[1]), int(argv[2]), int(argv[3]), 12)
    else:
        ts = utc() - datetime.timedelta(days=1)
        ts = ts.replace(hour=12, minute=0, second=0, microsecond=0)
    merge(ts)


if __name__ == "__main__":
    main(sys.argv)
