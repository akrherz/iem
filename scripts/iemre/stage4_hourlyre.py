""" Need something to push the stage4 data into the hourly files"""
from __future__ import print_function
import datetime
import os
import sys

import pygrib
import numpy as np
import pytz
import netCDF4
from scipy.interpolate import NearestNDInterpolator
from pyiem import iemre
from pyiem.util import utc


def to_netcdf(valid):
    """Persist this 1 hour precip information to the netcdf storage

    Recall that this timestep has data for the previous hour"""
    fn = ("/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib"
          ) % (valid.strftime("%Y/%m/%d"), valid.strftime("%Y%m%d%H"))
    if not os.path.isfile(fn):
        print("stage4_hourlyre: missing stageIV hourly file %s" % (fn, ))
        return False
    gribs = pygrib.open(fn)
    grb = gribs[1]
    val = grb.values
    # values over 10 inches are bad
    val = np.where(val > 250., 0, val)

    nc = netCDF4.Dataset(("/mesonet/data/stage4/%s_stage4_hourly.nc"
                          ) % (valid.year, ), 'a')
    tidx = iemre.hourly_offset(valid)
    if nc.variables['p01m_status'][tidx] > 1:
        print("Skipping stage4_hourlyre write as variable status is >1")
        nc.close()
        return True
    p01m = nc.variables['p01m']
    # account for legacy grid prior to 2002
    if val.shape == (880, 1160):
        p01m[tidx, 1:, :] = val[:, 39:]
    else:
        p01m[tidx, :, :] = val
    nc.variables['p01m_status'][tidx] = 1
    nc.close()

    return True


def merge(valid):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """
    nc = netCDF4.Dataset(("/mesonet/data/stage4/%s_stage4_hourly.nc"
                          ) % (valid.year, ), 'r')
    tidx = iemre.hourly_offset(valid)
    val = nc.variables['p01m'][tidx, :, :]
    # print("stage4 mean: %.2f max: %.2f" % (np.mean(val), np.max(val)))
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]

    # Rough subsample, since the whole enchillata is too much
    lats = np.ravel(lats[200:-100:5, 300:900:5])
    lons = np.ravel(lons[200:-100:5, 300:900:5])
    vals = np.ravel(val[200:-100:5, 300:900:5])
    nn = NearestNDInterpolator((lons, lats), vals)
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    res = nn(xi, yi)

    # Lets clip bad data
    # 10 inches per hour is bad data
    res = np.where(np.logical_or(res < 0, res > 250), 0., res)
    # print("Resulting mean: %.2f max: %.2f" % (np.mean(res), np.max(res)))

    # Open up our RE file
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (valid.year,),
                         'a')
    nc.variables["p01m"][tidx, :, :] = res
    # print(("Readback mean: %.2f max: %.2f"
    #       ) % (np.mean(nc.variables["p01m"][tidx, :, :]),
    #            np.max(nc.variables["p01m"][tidx, :, :])))
    nc.close()


def main(argv):
    """Go Main"""
    if len(argv) == 5:
        ts = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(minute=0, second=0, microsecond=0)
    ts = ts.replace(tzinfo=pytz.utc)

    if to_netcdf(ts):
        merge(ts)


if __name__ == "__main__":
    main(sys.argv)
