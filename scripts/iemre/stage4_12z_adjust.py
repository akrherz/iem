"""
  IEMRE precipitation is based off of the hourly stage IV precipitation
  Unfortunately, this is not heavily QC'd, so we use it as a function guide
  to the 12z data, which is of better quality 
"""

import pygrib
import datetime
import numpy
from pyiem import iemre
import sys
import netCDF4
import pytz

def merge(ts):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """

    # Load up the 12z 24h total, this is what we base our deltas on
    fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.24h.grib" % (
      ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H") )

    grib = Nio.open_file(fp, 'r')
    # Rough subsample, since the whole enchillata is too much
    lats = numpy.ravel( grib.variables["g5_lat_0"][200:-100:5,300:900:5] )
    lons = numpy.ravel( grib.variables["g5_lon_1"][200:-100:5,300:900:5] )
    vals = numpy.ravel( grib.variables["A_PCP_GDS5_SFC_acc24h"][200:-100:5,300:900:5] )
    res = Ngl.natgrid(lons, lats, vals, iemre.XAXIS, iemre.YAXIS)
    stage4 = res.transpose()
    # Prevent Large numbers, negative numbers
    stage4 = numpy.where( stage4 < 10000., stage4, 0.)
    stage4 = numpy.where( stage4 < 0., 0., stage4)

    # Open up our RE file
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_hourly.nc" % (ts.year,),'a')
    ts0 = ts - datetime.timedelta(days=1)
    offset0 = iemre.hourly_offset(ts0)
    offset1 = iemre.hourly_offset(ts)
    # Running at 12 UTC 1 Jan
    if offset0 > offset1:
        offset0 = 0
    iemre_total = numpy.sum(nc.variables["p01m"][offset0:offset1,:,:], axis=0)
    iemre_total = numpy.where( iemre_total > 0., iemre_total, 0.00024)
    iemre_total = numpy.where( iemre_total < 10000., iemre_total, 0.00024)
    print "Stage IV 24h [Avg %5.2f Max %5.2f]  IEMRE Hourly [Avg %5.2f Max: %5.2f]" % (
                    numpy.average(stage4), numpy.max(stage4), 
                    numpy.average(iemre_total), numpy.max(iemre_total) )
    multiplier = stage4 / iemre_total
    print "Multiplier MIN: %5.2f  AVG: %5.2f  MAX: %5.2f" % (
                    numpy.min(multiplier), numpy.average(multiplier),numpy.max(multiplier))
    for offset in range(offset0, offset1):
        # Get the unmasked dadta
        data  = nc.variables["p01m"][offset,:,:]
        
        # Keep data within reason
        data = numpy.where( data > 10000., 0., data)
        # 0.00024 / 24
        adjust = numpy.where( data > 0, data, 0.00001) * multiplier
        adjust = numpy.where( adjust > 250.0, 0, adjust)
        nc.variables["p01m"][offset,:,:] = numpy.where( adjust < 0.01, 0, adjust)
        ts = ts0 + datetime.timedelta(hours=offset-offset0)
        print "%s IEMRE %5.2f %5.2f Adjusted %5.2f %5.2f" % (ts.strftime("%Y-%m-%d %H"), 
                                    numpy.average(data), numpy.max(data),
                                    numpy.average(nc.variables["p01m"][offset]),
                                    numpy.max(nc.variables["p01m"][offset]))
    nc.sync()
    iemre2 = numpy.sum(nc.variables["p01m"][offset0:offset1,:,:], axis=0)
    print "Stage IV 24h [Avg %5.2f Max %5.2f]  IEMRE Hourly [Avg %5.2f Max: %5.2f]" % (
                    numpy.average(stage4), numpy.max(stage4), 
                    numpy.average(iemre2), numpy.max(iemre2) )
    nc.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ts = datetime.datetime( int(sys.argv[1]),int(sys.argv[2]),
                           int(sys.argv[3]), 12 )
    else:
        ts = datetime.datetime.utcnow()
        ts = ts - datetime.timedelta(days=1) 
        ts = ts.replace(hour=12,minute=0,second=0, microsecond=0)
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    merge(ts)

