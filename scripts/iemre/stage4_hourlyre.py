# Need something to push the stage4 data into the hourly files

import Nio
import mx.DateTime
import Ngl
import numpy
import constants
import os
import sys
import netCDF3

def merge(ts):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """

    fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib" % (
      ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H") )

    grib = Nio.open_file(fp, 'r')
    # Rough subsample, since the whole enchillata is too much
    lats = numpy.ravel( grib.variables["g5_lat_0"][400:-300,500:700] )
    lons = numpy.ravel( grib.variables["g5_lon_1"][400:-300,500:700] )
    vals = numpy.ravel( grib.variables["A_PCP_GDS5_SFC_acc1h"][400:-300,500:700] )
    res = Ngl.natgrid(lons, lats, vals, constants.XAXIS, constants.YAXIS)

    # Open up our RE file
    nc = netCDF3.Dataset("/mnt/mesonet/data/iemre/%s_hourly.nc" % (ts.year,),'a')

    offset = int(( ts - (ts + mx.DateTime.RelativeDateTime(month=1,day=1,hour=0))).hours) - 1
    nc.variables["p01m"][offset,:,:] = res.transpose()

    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 5:
        ts = mx.DateTime.DateTime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]), int(sys.argv[4]) )
    else:
        ts = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minute=0,second=0)
    merge(ts)

