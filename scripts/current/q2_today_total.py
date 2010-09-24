"""
Create a plot of today's total precipitation from the Stage4 estimates
"""

import netCDF3
import mx.DateTime
import iemplot
import numpy
import os, sys

def doday(ts):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    sts = ts + mx.DateTime.RelativeDateTime(hour=1, minute=0)
    ets = ts + mx.DateTime.RelativeDateTime(hour=1, days=1, minute=0)
    interval = mx.DateTime.RelativeDateTime(hours=1)
    now = sts
    total = None
    lts = None
    lons = numpy.arange(-110., -89.99, 0.01) 
    lats = numpy.arange(55.0, 39.99, -0.01)
    ncvar = "rad_hsr_1h"
    divisor = 1.0

    while now < ets:
        fp = "/mnt/a1/ARCHIVE/data/%s/q2/tile2/q2rad_hsr_nc/short_qpe/%s0000.nc" % (
            now.gmtime().strftime("%Y/%m/%d"), 
            now.gmtime().strftime("%Y%m%d%H") )
        if os.path.isfile(fp):
            print "USING %s NCVAR %s DIVISOR %s" % (fp, ncvar, divisor)
            lts = now
            nc = netCDF3.Dataset(fp)
            val = nc.variables[ncvar][:] / divisor
            if total is None:
                total = numpy.where(val > 0, val, 0) 
            else:
                total += numpy.where( val > 0, val, 0)
            
            nc.close()
        # Now we need to go start looking at the 5 minute files
        if now.hour == ts.hour:
            interval = mx.DateTime.RelativeDateTime(minutes=5)
            ets = now + mx.DateTime.RelativeDateTime(hours=1)
            ncvar = "preciprate_hsr"
            divisor = 12.0
        now += interval
        
    # Now we dance
    cfg = { 
    'cnLevelSelectionMode': "ExplicitLevels",
    'cnLevels' : [0.01,0.1,0.25,0.5,0.75,1,1.5,2,3,4,5,8,10,15,20],
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     'lbTitleString'      : "[inch]",
     '_valid'    : 'Total up to %s' % (
        (lts - mx.DateTime.RelativeDateTime(minutes=1)).strftime("%d %B %Y %I:%M %p %Z"),),
     '_title'    : "NMQ Q2 Today's Precipitation [inch]",
    }

    # Scale factor is 10
    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 254.0, cfg)
    pqstr = "plot ac %s00 iowa_q2_1d.png iowa_q2_1d.png png" % (
            ts.strftime("%Y%m%d%H"), )
    iemplot.postprocess(tmpfp, pqstr)
    
    
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        doday(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
    else:
        doday(mx.DateTime.now())