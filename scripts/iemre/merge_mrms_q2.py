'''
Merge the 1km Q2 24 hour precip data estimates
'''
import datetime
import pytz
import sys
import pyiem.mrms as mrms
import netCDF4
import numpy as np
from PIL import Image
from pyiem import iemre


def run(ts):
    ''' Actually do the work, please '''
    nc = netCDF4.Dataset('/mesonet/data/iemre/%s_mw_mrms_daily.nc' % (
                                                            ts.year,),
                         'a')
    offset = iemre.daily_offset(ts)
    ncprecip = nc.variables['p01d']
    ts += datetime.timedelta(hours=24)
    gmtts = ts.astimezone(pytz.timezone("UTC"))

    fn = gmtts.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/q2/"
                        "p24h_%Y%m%d%H00.png"))
    img = Image.open(fn)
    data = np.asarray(img)
    # data is 3500,7000 , starting at upper L
    data = np.flipud(data)
    # Anything over 254 is bad
    res = np.where(data > 254, 0, data)
    res = np.where(np.logical_and(data >= 0, data < 100), data * 0.25, res)
    res = np.where(np.logical_and(data >= 100, data < 180),
                   25. + ((data - 100) * 1.25), res)
    res = np.where(np.logical_and(data >= 180, data < 255),
                   125. + ((data - 180) * 5.), res)

    y1 = (iemre.NORTH - mrms.SOUTH) * 100.0
    y0 = (iemre.SOUTH - mrms.SOUTH) * 100.0
    x0 = (iemre.WEST - mrms.WEST) * 100.0
    x1 = (iemre.EAST - mrms.WEST) * 100.0
    ncprecip[offset, :, :] = res[y0:y1, x0:x1]
    nc.close()

if __name__ == '__main__':
    if len(sys.argv) == 4:
        # 12 noon to prevent ugliness with timezones
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), 12, 0)
    else:
        ts = datetime.datetime.now() - datetime.timedelta(hours=24)
        ts = ts.replace(hour=12)

    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    ts = ts.astimezone(pytz.timezone("America/Chicago"))
    ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    run(ts)
