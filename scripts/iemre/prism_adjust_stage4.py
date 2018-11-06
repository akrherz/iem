"""So we are here, this is our life...

Take the PRISM data, valid at 12z and bias correct the hourly stage IV data

"""
from __future__ import print_function
import sys
import datetime

import numpy as np
from scipy.interpolate import NearestNDInterpolator
from pyiem.iemre import daily_offset, hourly_offset
from pyiem.util import utc, ncopen


def workflow(valid):
    """Our workflow"""
    if valid.month == 1 and valid.day == 1:
        print("prism_adjust_stage4, sorry Jan 1 processing is a TODO!")
        return
    # read prism
    tidx = daily_offset(valid)
    nc = ncopen("/mesonet/data/prism/%s_daily.nc" % (valid.year, ), 'r')
    ppt = nc.variables['ppt'][tidx, :, :]
    # missing as zero
    ppt = np.where(ppt.mask, 0, ppt)
    lons = nc.variables['lon'][:]
    lats = nc.variables['lat'][:]
    nc.close()
    (lons, lats) = np.meshgrid(lons, lats)

    # Interpolate this onto the stage4 grid
    nc = ncopen(("/mesonet/data/stage4/%s_stage4_hourly.nc"
                 ) % (valid.year, ), 'a', timeout=300)
    p01m = nc.variables['p01m']
    p01m_status = nc.variables['p01m_status']
    s4lons = nc.variables['lon'][:]
    s4lats = nc.variables['lat'][:]
    # Values are in the hourly arrears, so start at -23 and thru current hour
    sts_tidx = hourly_offset(valid - datetime.timedelta(hours=23))
    ets_tidx = hourly_offset(valid + datetime.timedelta(hours=1))
    s4total = np.sum(p01m[sts_tidx:ets_tidx, :, :], axis=0)
    # make sure the s4total does not have zeros
    s4total = np.where(s4total < 0.001, 0.001, s4total)

    nn = NearestNDInterpolator((lons.flatten(), lats.flatten()), ppt.flat)
    prism_on_s4grid = nn(s4lons, s4lats)
    multiplier = prism_on_s4grid / s4total

    # Do the work now, we should not have to worry about the scale factor
    for tidx in range(sts_tidx, ets_tidx):
        oldval = p01m[tidx, :, :]
        # we threshold the s4total to at least 0.001, so we divide by 24 here
        # and denote that if the multiplier is zero, then we net zero
        newval = np.where(oldval < 0.001, 0.00004, oldval) * multiplier
        p01m[tidx, :, :] = newval
        # make sure have data
        if np.ma.max(newval) > 0:
            p01m_status[tidx] = 2
        else:
            print(("prism_adjust_stage4 NOOP for time %s[idx:%s]"
                   ) % ((datetime.datetime(valid.year, 1, 1, 0) +
                         datetime.timedelta(hours=tidx)
                         ).strftime("%Y-%m-%dT%H"), tidx))

    """
    s4total_v2 = np.sum(p01m[sts_tidx:ets_tidx, :, :], axis=0)

    from pyiem.plot.geoplot import MapPlot
    import matplotlib.pyplot as plt
    mp = MapPlot(sector='iowa')
    mp.pcolormesh(s4lons, s4lats, s4total_v2,
                  np.arange(-10, 11, 1), cmap=plt.get_cmap("BrBG"))
    mp.postprocess(filename='test.png')
    mp.close()
    """
    nc.close()


def main(argv):
    """Go Main"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), 12)
    workflow(valid)


if __name__ == '__main__':
    main(sys.argv)
