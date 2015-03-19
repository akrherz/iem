# Need something to push the stage4 data into the hourly files

import pygrib
import datetime
import numpy as np
from pyiem import iemre
import os
import sys
import pytz
import netCDF4
from scipy.interpolate import NearestNDInterpolator


def merge(ts):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """

    fn = ("/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib"
          ) % (ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H"))
    if os.path.isfile(fn):
        gribs = pygrib.open(fn)
        grb = gribs[1]
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
        res = nn(xi, yi)
    else:
        print 'Missing stage4 %s' % (fn,)
        res = np.zeros((iemre.NX, iemre.NY))

    # Lets clip bad data
    res = np.where(res < 0, 0., res)
    # 10 inches per hour is bad data
    res = np.where(res > 250., 0., res)

    # Open up our RE file
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,),
                         'a')
    offset = iemre.hourly_offset(ts)
    nc.variables["p01m"][offset, :, :] = res

    nc.close()
    del nc


def main():
    """Go Main"""
    if len(sys.argv) == 5:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), int(sys.argv[4]))
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(minute=0, second=0, microsecond=0)
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    merge(ts)

if __name__ == "__main__":
    main()
