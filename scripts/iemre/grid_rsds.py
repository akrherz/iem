"""Do the gridding of Solar Radiation Data

Called from RUN_2AM.sh
"""
import netCDF4
import pygrib
import pyproj
import datetime
import pytz
import os
import sys
import numpy as np
from pyiem import iemre

P4326 = pyproj.Proj(init="epsg:4326")
LCC = pyproj.Proj(("+lon_0=-97.5 +y_0=0.0 +R=6367470. +proj=lcc +x_0=0.0"
                   " +units=m +lat_2=38.5 +lat_1=38.5 +lat_0=38.5"))

SWITCH_DATE = datetime.datetime(2014, 10, 10, 20)
SWITCH_DATE = SWITCH_DATE.replace(tzinfo=pytz.timezone("UTC"))


def do_hrrr(ts):
    """Convert the hourly HRRR data to IEMRE grid"""
    total = None
    xaxis = None
    yaxis = None
    for hr in range(5, 23):  # Only need 5 AM to 10 PM for solar
        utc = ts.replace(hour=hr).astimezone(pytz.timezone("UTC"))
        fn = utc.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                           "hrrr.t%Hz.3kmf00.grib2"))
        if not os.path.isfile(fn):
            # print 'HRRR file %s missing' % (fn,)
            continue
        grbs = pygrib.open(fn)
        try:
            if utc >= SWITCH_DATE:
                grb = grbs.select(name='Downward short-wave radiation flux')
            else:
                grb = grbs.select(parameterNumber=192)
        except ValueError:
            print 'coop/hrrr_solarrad.py %s had no solar rad' % (fn,)
            continue
        if len(grb) == 0:
            print 'Could not find SWDOWN in HRR %s' % (fn,)
            continue
        g = grb[0]
        if total is None:
            total = g.values
            lat1 = g['latitudeOfFirstGridPointInDegrees']
            lon1 = g['longitudeOfFirstGridPointInDegrees']
            llcrnrx, llcrnry = LCC(lon1, lat1)
            nx = g['Nx']
            ny = g['Ny']
            dx = g['DxInMetres']
            dy = g['DyInMetres']
            xaxis = llcrnrx + dx * np.arange(nx)
            yaxis = llcrnry + dy * np.arange(ny)
        else:
            total += g.values

    if total is None:
        print 'coop/hrrr_solarrad.py found no HRRR data for %s' % (
                                                    ts.strftime("%d %b %Y"), )
        return

    # We wanna store as W m-2, so we just average out the data by hour
    total = total / 24.0

    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year,),
                         'a')
    offset = iemre.daily_offset(ts)
    data = nc.variables['rsds'][offset, :, :]
    print np.shape(total), np.shape(data)
    for i, lon in enumerate(iemre.XAXIS):
        for j, lat in enumerate(iemre.YAXIS):
            (x, y) = LCC(lon, lat)
            i2 = np.digitize([x], xaxis)[0]
            j2 = np.digitize([y], yaxis)[0]
            data[j, i] = total[j2, i2]

    nc.variables['rsds'][offset] = data
    nc.close()

if __name__ == '__main__':
    if len(sys.argv) == 4:
        sts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                                int(sys.argv[3]), 12)
    else:
        sts = datetime.datetime.now() - datetime.timedelta(days=1)
        sts = sts.replace(hour=12)
    sts = sts.replace(tzinfo=pytz.timezone("America/Chicago"))
    do_hrrr(sts)
