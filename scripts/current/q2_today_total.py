"""
Create a plot of today's total precipitation from the Stage4 estimates
"""

import netCDF4
import mx.DateTime
import numpy
import os
import sys

from iem.plot import MapPlot

def make_fp(ts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile2/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
        ts.gmtime().strftime("%Y/%m/%d"), 
        ts.gmtime().strftime("%Y%m%d-%H%M") )

def doday(ts):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # First possible file we are interested in....
    sts = ts + mx.DateTime.RelativeDateTime(hour=1, minute=0)
    # Last possible file, base 5
    ets = ts - mx.DateTime.RelativeDateTime(minutes= (ts.minute%5))
    
    now = ets
    total = None
    lts = None
    lons = numpy.arange(-110., -89.995, 0.01) 
    lats = numpy.arange(55.0, 39.99, -0.01)
    ncvar = "rad_hsr_1h"
    divisor = 1.0
    interval = mx.DateTime.RelativeDateTime(minutes=5)

    while now > sts:
        if os.path.isfile(make_fp(now)):
            if lts is None:
                lts = now
            if now.minute == 0:
                ncvar = "rad_hsr_1h"
                divisor = 1.0
                interval = mx.DateTime.RelativeDateTime(hours=1)
            else:
                ncvar = "preciprate_hsr"
                divisor = 12.0
            #print "USING %s NCVAR %s DIVISOR %s" % (make_fp(now), 
            #                                        ncvar, divisor)
            nc = netCDF4.Dataset(make_fp(now))
            if nc.variables.has_key(ncvar):
                val = nc.variables[ncvar][:] / divisor
                if total is None:
                    total = numpy.where(val > 0, val, 0)
                    #total = val
                else:
                    total += numpy.where( val > 0, val, 0)
                    #total += val
            nc.close()
        now -= interval
    
    if total is None:
        return
   
    subtitle = 'Total up to %s' % (
        (lts - mx.DateTime.RelativeDateTime(minutes=1))
        .strftime("%d %B %Y %I:%M %p %Z"),)
    pqstr = "plot ac %s00 iowa_q2_1d.png iowa_q2_1d.png png" % (
            ts.strftime("%Y%m%d%H"), )
    m = MapPlot(title="NMQ Q2 Today's Precipitation [inch]",
                subtitle=subtitle, pqstr=pqstr)
        
    clevs = numpy.arange(0,0.2,0.05)
    clevs = numpy.append(clevs, numpy.arange(0.2, 1.0, 0.1))
    clevs = numpy.append(clevs, numpy.arange(1.0, 5.0, 0.25))
    clevs = numpy.append(clevs, numpy.arange(5.0, 10.0, 1.0))
    clevs[0] = 0.01

    m.contourf(lons, lats, total / 254.0, clevs)

    #map.drawstates(zorder=2)
    m.drawcounties()
    m.postprocess()    
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        doday(mx.DateTime.DateTime(int(sys.argv[1]), 
                                   int(sys.argv[2]), int(sys.argv[3]), 23, 55))
    else:
        doday(mx.DateTime.now())
