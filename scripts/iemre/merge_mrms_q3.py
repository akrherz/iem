'''
Merge the 1km Q3 24 hour precip data estimates
'''
import gzip
import datetime
import pytz
import sys
sys.path.insert(0, '../mrms')
import util
import os
import netCDF4
import numpy as np
from pyiem import iemre
#import matplotlib.pyplot as plt

def run( ts ):
    ''' Actually do the work, please '''
    nc = netCDF4.Dataset('/mesonet/data/iemre/%s_mw_mrms_daily.nc' % (ts.year,), 
                         'a')
    offset = iemre.daily_offset(ts)
    ncprecip = nc.variables['p01d']

    mrms = np.zeros( (3500,7000), 'f')
    ts += datetime.timedelta(hours=24)
    gmtts = ts.astimezone( pytz.timezone("UTC") )

    for tile in range(1,5):
        fn = util.get_fn('24hrad', gmtts, tile)
        if not os.path.isfile(fn):
            print "24h Tile: %s Time: %s UTC %s" % (tile, 
                                        gmtts.strftime("%Y-%m-%d %H:%M"), fn)
            continue
        tilemeta, val = util.reader(fn)
        
        ysz, xsz = np.shape(val)
        x0 = (tilemeta['ul_lon'] - util.WEST) * 100.0
        y0 = (util.NORTH - tilemeta['ul_lat']) * 100.0
        mrms[y0:(y0+ysz),x0:(x0+xsz)] = np.flipud(val)

    # the MRMS array starts at upper left hand corner
    # y0 is northmost
    y0 = (util.NORTH - iemre.NORTH) * 100.0
    y1 = (util.NORTH - iemre.SOUTH) * 100.0
    x0 = (iemre.WEST - util.WEST) * 100.0
    x1 = (iemre.EAST - util.WEST) * 100.0
    #print 'y0:%s y1:%s x0:%s x1:%s' % (y0, y1, x0, x1)
    ncprecip[offset,:,:] = mrms[y0:y1,x0:x1]
    #(fig, ax) = plt.subplots()
    #ax.imshow(mrms)
    #fig.savefig('test.png')
    #(fig, ax) = plt.subplots()
    #ax.imshow(mrms[y0:y1,x0:x1])
    #fig.savefig('test2.png')
    nc.close()

if __name__ == '__main__':
    if len(sys.argv) == 4:
        # 12 noon to prevent ugliness with timezones
        ts = datetime.datetime( int(sys.argv[1]), int(sys.argv[2]),
                                int(sys.argv[3]), 12, 0 )
    else:
        ts = datetime.datetime.now() - datetime.timedelta(hours=24)
        ts = ts.replace(hour=12)
    
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    ts = ts.astimezone( pytz.timezone("America/Chicago") )
    ts = ts.replace(hour=0,minute=0,second=0,microsecond=0)
    run( ts )
        
        