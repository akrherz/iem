"""
Merge the 1km Q3 24 hour precip data estimates
"""
import datetime
import pytz
import sys
sys.path.insert(0, '../mrms')
import util
import os
import netCDF4
import numpy as np
from pyiem import iemre
import pygrib
import gzip
import tempfile
#from pyiem.plot import MapPlot

def run(ts):
    """ Actually do the work, please """
    nc = netCDF4.Dataset('/mesonet/data/iemre/%s_mw_mrms_daily.nc' % (
                                                            ts.year,), 'a')
    offset = iemre.daily_offset(ts)
    ncprecip = nc.variables['p01d']

    # We want this mrms variable to replicate the netcdf file, so the
    # origin is the southwestern corner
    ts += datetime.timedelta(hours=24)
    gmtts = ts.astimezone(pytz.timezone("UTC"))

    gribfn = gmtts.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/"
            +"RadarOnly_QPE_24H/"
            +"RadarOnly_QPE_24H_00.00_%Y%m%d-%H%M00.grib2.gz"))
    if not os.path.isfile(gribfn):
        print("merge_mrms_q3.py MISSING %s" % (gribfn,))
        return

    fp = gzip.GzipFile(gribfn, 'rb')
    (tmpfp, tmpfn) = tempfile.mkstemp()
    tmpfp = open(tmpfn, 'wb')
    tmpfp.write(fp.read())
    tmpfp.close()
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    os.unlink(tmpfn)

    mrms = grb['values']
    # Anything less than zero, we set to zero
    mrms = np.where(mrms < 0, 0, mrms)

    # Figure out what we wish to subsample
    y0 = int((iemre.SOUTH - util.SOUTH) * 100.0)
    y1 = int((iemre.NORTH - util.SOUTH) * 100.0)
    x0 = int((iemre.WEST - util.WEST) * 100.0)
    x1 = int((iemre.EAST - util.WEST) * 100.0)
    #print 'y0:%s y1:%s x0:%s x1:%s' % (y0, y1, x0, x1)
    ncprecip[offset, :, :] = mrms[y0:y1, x0:x1]
    #m = MapPlot(sector='midwest')
    #x, y = np.meshgrid(nc.variables['lon'][:], nc.variables['lat'][:])
    #m.pcolormesh(x, y, ncprecip[offset,:,:], range(10), latlon=True)
    #m.postprocess(filename='test.png')
    #(fig, ax) = plt.subplots()
    #ax.imshow(mrms)
    #fig.savefig('test.png')
    #(fig, ax) = plt.subplots()
    #ax.imshow(mrms[y0:y1,x0:x1])
    #fig.savefig('test2.png')
    nc.close()

def main():
    """ go main go """
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

if __name__ == '__main__':
    main()