"""
We need to use the QC'd 24h 12z total to fix the 1h problems :(
"""
from __future__ import print_function
import sys
import datetime

import numpy as np
import netCDF4
import pytz
from scipy.interpolate import NearestNDInterpolator
import pygrib
from pyiem import iemre


def merge(ts):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """

    # Load up the 12z 24h total, this is what we base our deltas on
    fn = ("/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.24h.grib"
          ) % (ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H"))

    grbs = pygrib.open(fn)
    grb = grbs[1]
    val = grb.values
    lats, lons = grb.latlons()
    # Rough subsample, since the whole enchillata is too much
    lats = np.ravel(lats[200:-100:5, 300:900:5])
    lons = np.ravel(lons[200:-100:5, 300:900:5])
    vals = np.ravel(val[200:-100:5, 300:900:5])
    # Clip large values
    vals = np.where(vals > 250., 0, vals)
    nn = NearestNDInterpolator((lons, lats), vals)
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    stage4 = nn(xi, yi)
    # Prevent Large numbers, negative numbers
    stage4 = np.where(stage4 < 10000., stage4, 0.)
    stage4 = np.where(stage4 < 0., 0., stage4)

    # Open up our RE file
    nc = netCDF4.Dataset(iemre.get_hourly_ncname(ts.year), 'a')
    ts0 = ts - datetime.timedelta(days=1)
    offset0 = iemre.hourly_offset(ts0)
    offset1 = iemre.hourly_offset(ts)
    # Running at 12 UTC 1 Jan
    if offset0 > offset1:
        offset0 = 0
    iemre_total = np.sum(nc.variables["p01m"][offset0:offset1, :, :], axis=0)
    iemre_total = np.where(iemre_total > 0., iemre_total, 0.00024)
    iemre_total = np.where(iemre_total < 10000., iemre_total, 0.00024)
    multiplier = stage4 / iemre_total
    for offset in range(offset0, offset1):
        # Get the unmasked dadta
        data = nc.variables["p01m"][offset, :, :]

        # Keep data within reason
        data = np.where(data > 10000., 0., data)
        # 0.00024 / 24
        adjust = np.where(data > 0, data, 0.00001) * multiplier
        adjust = np.where(adjust > 250.0, 0, adjust)
        nc.variables["p01m"][offset, :, :] = np.where(adjust < 0.01, 0, adjust)
        ts = ts0 + datetime.timedelta(hours=offset-offset0)
    nc.sync()
    nc.close()


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        ts = datetime.datetime(int(argv[1]), int(argv[2]),
                               int(argv[3]), 12)
    else:
        ts = datetime.datetime.utcnow()
        ts = ts - datetime.timedelta(days=1)
        ts = ts.replace(hour=12, minute=0, second=0, microsecond=0)
    ts = ts.replace(tzinfo=pytz.utc)
    merge(ts)


if __name__ == "__main__":
    main(sys.argv)
