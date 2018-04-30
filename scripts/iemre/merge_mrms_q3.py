"""Merge the 0.01x0.01 Q3 24 hour precip data estimates"""
from __future__ import print_function
import datetime
import sys
import os
import gzip
import tempfile

import pytz
import netCDF4
import numpy as np
import requests
import pygrib
import pyiem.mrms as mrms
from pyiem import iemre

TMP = "/mesonet/tmp"


def run(ts):
    """Update netcdf file with the MRMS data

    Args:
      ts (datetime): timestamptz at midnight central time and we are running
        forward in time
    """
    nc = netCDF4.Dataset(('/mesonet/data/iemre/%s_mw_mrms_daily.nc'
                          '') % (ts.year,), 'a')
    nc.set_auto_scale(True)
    offset = iemre.daily_offset(ts)
    ncprecip = nc.variables['p01d']

    gmtts = ts.astimezone(pytz.utc)
    utcnow = datetime.datetime.utcnow().replace(minute=0, second=0,
                                                microsecond=0)
    utcnow = utcnow.replace(tzinfo=pytz.utc)

    total = None
    lats = None
    for _ in range(1, 25):
        gmtts += datetime.timedelta(hours=1)
        gribfn = None
        for prefix in ['GaugeCorr', 'RadarOnly']:
            fn = gmtts.strftime((prefix + "_QPE_01H_00.00_%Y%m%d-%H%M00"
                                 ".grib2.gz"))
            url = gmtts.strftime(
                    ("http://mtarchive.geol.iastate.edu/%Y/%m/%d/mrms/ncep/" +
                     prefix + "_QPE_01H/" + fn))
            res = requests.get(url, timeout=30)
            if res.status_code != 200:
                continue
            gribfn = "%s/%s" % (TMP, fn)
            output = open(gribfn, 'wb')
            output.write(res.content)
            output.close()
            break
        if gribfn is None:
            if gmtts < utcnow:
                print("merge_mrms_q3.py MISSING %s" % (gmtts, ))
            continue
        # print("Using -> %s" % (gribfn,))
        fp = gzip.GzipFile(gribfn, 'rb')

        (_, tmpfn) = tempfile.mkstemp()
        tmpfp = open(tmpfn, 'wb')
        tmpfp.write(fp.read())
        tmpfp.close()
        grbs = pygrib.open(tmpfn)
        grb = grbs[1]
        if lats is None:
            lats, _ = grb.latlons()
        os.unlink(tmpfn)

        val = grb['values']
        # Anything less than zero, we set to zero
        val = np.where(val < 0, 0, val)
        if total is None:
            total = val
        else:
            total += val

        os.unlink(gribfn)

    # CAREFUL HERE!  The MRMS grid is North to South
    # set top (smallest y)
    y0 = int((lats[0, 0] - 49.0) * 100.0)
    y1 = int((lats[0, 0] - 36.0) * 100.0)
    x0 = int((-104.0 - mrms.WEST) * 100.0)
    x1 = int((-80.5 - mrms.WEST) * 100.0)
    # print 'y0:%s y1:%s x0:%s x1:%s lat0:%s offset:%s ' % (y0, y1, x0, x1,
    #                                                      lats[0, 0], offset)
    ncprecip[offset, :, :] = np.flipud(total[y0:y1, x0:x1])
    nc.close()


def main(argv):
    """ go main go """
    if len(argv) == 4:
        # 12 noon to prevent ugliness with timezones
        ts = datetime.datetime(int(argv[1]), int(argv[2]),
                               int(argv[3]), 12, 0)
    else:
        # default to noon today
        ts = datetime.datetime.now()
        ts = ts.replace(hour=12)

    ts = ts.replace(tzinfo=pytz.utc)
    ts = ts.astimezone(pytz.timezone("America/Chicago"))
    ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    run(ts)


if __name__ == '__main__':
    main(sys.argv)
