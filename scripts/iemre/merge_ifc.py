"""Merge the PNG IFC files into the daily netcdf file"""
from pyiem import iemre
import datetime
import sys
import netCDF4
import pytz
import os
from osgeo import gdal
import numpy as np


def run(ts):
    """Process this date's worth of data"""
    now = ts.replace(hour=0, minute=0)
    ets = now + datetime.timedelta(hours=24)
    interval = datetime.timedelta(minutes=5)
    currenttime = datetime.datetime.utcnow()
    currenttime = currenttime.replace(tzinfo=pytz.timezone("UTC"))

    total = None
    while now <= ets:
        gmt = now.astimezone(pytz.timezone("UTC"))
        if gmt > currenttime:
            break
        fn = gmt.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/"
                           "GIS/ifc/p05m_%Y%m%d%H%M.png"))
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
        print(('No IFC Data found for date: %s'
               ) % (now.strftime("%d %B %Y"),))
        return

    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_ifc_daily.nc" % (ts.year,),
                         "a")
    idx = iemre.daily_offset(ts)
    nc.variables['p01d'][idx, :, :] = np.flipud(total)
    nc.close()


def main(argv):
    if len(argv) == 4:
        date = datetime.datetime(int(argv[1]), int(argv[2]),
                                 int(argv[3]), 12, 0)
    else:
        date = datetime.datetime.now()
        date = date - datetime.timedelta(minutes=60)
        date = date.replace(hour=12, minute=0, second=0, microsecond=0)
    # Stupid pytz timezone dance
    date = date.replace(tzinfo=pytz.timezone("UTC"))
    date = date.astimezone(pytz.timezone("America/Chicago"))
    run(date)


if __name__ == "__main__":
    main(sys.argv)
