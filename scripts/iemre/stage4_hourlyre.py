# Need something to push the stage4 data into the hourly files

import Nio
import mx.DateTime
import Ngl
import numpy
import iemre
import os
import sys
try:
    import netCDF3
except:
    import netCDF4 as netCDF3

def merge(ts):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """

    fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib" % (
      ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H") )
    if os.path.isfile(fp):
        grib = Nio.open_file(fp, 'r')
        # Rough subsample, since the whole enchillata is too much
        lats = numpy.ravel( grib.variables["g5_lat_0"][200:-100:5,300:900:5] )
        lons = numpy.ravel( grib.variables["g5_lon_1"][200:-100:5,300:900:5] )
        vals = numpy.ravel( grib.variables["A_PCP_GDS5_SFC_acc1h"][200:-100:5,300:900:5] )
        # Clip large values
        vals = numpy.where( vals > 250., 0, vals)
        #print 'STAGE4 MIN: %5.2f AVG: %5.2f MAX: %5.2f' % (numpy.min(vals), numpy.average(vals),
        #                                           numpy.max(vals))
        res = Ngl.natgrid(lons, lats, vals, iemre.XAXIS, iemre.YAXIS)
        grib.close()
        del grib
    else:
        print 'Missing stage4 %s' % (fp,)
        res = numpy.zeros( (iemre.NX, iemre.NY))

    # Lets clip bad data
    res = numpy.where(res < 0, 0., res)
    # 10 inches per hour is bad data
    res = numpy.where(res > 250., 0., res)

    # Print out some debugging information for now
    #print '%s MIN: %5.2f AVG: %5.2f MAX: %5.2f' % (ts, numpy.min(res), numpy.average(res),
    #                                               numpy.max(res))
    # Open up our RE file
    nc = netCDF3.Dataset("/mnt/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,),'a')

    offset = int(( ts - (ts + mx.DateTime.RelativeDateTime(month=1,day=1,hour=0))).hours) - 1
    nc.variables["p01m"][offset,:,:] = res.transpose()

    nc.close()
    del nc

if __name__ == "__main__":
    if len(sys.argv) == 5:
        ts = mx.DateTime.DateTime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]), int(sys.argv[4]) )
    else:
        ts = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minute=0,second=0)
    merge(ts)

