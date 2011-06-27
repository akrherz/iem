"""
We need to use the QC'd 24h 12z total to fix the 1h problems :(
"""

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

    fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.24h.grib" % (
      ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H") )

    grib = Nio.open_file(fp, 'r')
    # Rough subsample, since the whole enchillata is too much
    lats = numpy.ravel( grib.variables["g5_lat_0"][400:-300,500:700] )
    lons = numpy.ravel( grib.variables["g5_lon_1"][400:-300,500:700] )
    vals = numpy.ravel( grib.variables["A_PCP_GDS5_SFC_acc24h"][400:-300,500:700] )
    res = Ngl.natgrid(lons, lats, vals, constants.XAXIS, constants.YAXIS)
    good = res.transpose()
    # Prevent Large numbers
    good = numpy.where( good < 10000., good, 0.)

    # Open up our RE file
    nc = netCDF3.Dataset("/mesonet/data/iemre/%s_hourly.nc" % (ts.year,),'a')
    ts0 = ts + mx.DateTime.RelativeDateTime(days=-1)
    jan1 = mx.DateTime.DateTime(ts.year, 1, 1, 0, 0)
    offset0 = int(( ts0 - jan1).hours)
    offset1 = int(( ts -  jan1).hours)
    bad = numpy.sum(nc.variables["p01m"][offset0:offset1,:,:], axis=0)
    bad.set_fill_value(0.)
    bad = numpy.where( bad > 0., bad, 0.00024)
    bad = numpy.where( bad < 10000., bad, 0.00024)
    print "Stage IV 24h [Avg %5.2f Max %5.2f]  IEMRE Hourly [Avg %5.2f Max: %5.2f]" % (
                    numpy.average(good), numpy.max(good), 
                    numpy.average(bad), numpy.max(bad) )
    for offset in range(offset0, offset1):
        data  = nc.variables["p01m"][offset,:,:]
        
        # Keep data within reason
        data = numpy.where( data > 10000., 0., data)
        adjust = numpy.where( data > 0, data, 0.00001) / bad * good
        adjust = numpy.where( adjust > 250.0, 0, adjust)
        nc.variables["p01m"][offset,:,:] = numpy.where( adjust < 0.01, 0, adjust)
        ts = jan1 + mx.DateTime.RelativeDateTime(hours=offset)
        print "%s IEMRE %5.2f %5.2f Adjusted %5.2f %5.2f" % (ts.strftime("%Y-%m-%d %H"), 
                                    numpy.average(data), numpy.max(data),
                                    numpy.average(nc.variables["p01m"][offset]),
                                    numpy.max(nc.variables["p01m"][offset]))
    nc.sync()
    bad = numpy.sum(nc.variables["p01m"][offset0:offset1,:,:], axis=0)
    print "Stage IV 24h [Avg %5.2f Max %5.2f]  IEMRE Hourly [Avg %5.2f Max: %5.2f]" % (
                    numpy.average(good), numpy.max(good), 
                    numpy.average(bad), numpy.max(bad) )
    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ts = mx.DateTime.DateTime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]), 12 )
    else:
        ts = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(days=-1,hour=12,minute=0,second=0)
    merge(ts)

