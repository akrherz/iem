"""
Create a plot of the X Hour interval precipitation
"""

import netCDF3
import mx.DateTime
import iemplot
import numpy
import os, sys

def make_fp(ts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile2/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
        ts.strftime("%Y/%m/%d"), 
        ts.strftime("%Y%m%d-%H%M") )

def doit(ts, hours):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Mod the minute down
    remain = ts.minute % 5
    ts -= mx.DateTime.RelativeDateTime(minutes=(ts.minute%5))
    
    lons = numpy.arange(-110., -89.99, 0.01) 
    lats = numpy.arange(55.0, 39.99, -0.01)

    limit = 20
    while not os.path.isfile(make_fp(ts)):
        ts -= mx.DateTime.RelativeDateTime(minutes=5)
        if limit == 0:
            print "NO Q2 Files Found!"
            return
        limit -= 1
    total = None
    for hr in range(hours):
        lts = ts - mx.DateTime.RelativeDateTime(hours=hr)
        nc = netCDF3.Dataset(make_fp(lts))
        if hr == 0:
            total = nc.variables["rad_hsr_1h"][:]
        else:
            total += nc.variables["rad_hsr_1h"][:]
        nc.close()
    # Put some bad values in just to make the plot happy
    total[1350,1610] = 100.0
    total[1410,1675] = 15.
        
    # Now we dance
    cfg = { 
    'cnLevelSelectionMode': "ExplicitLevels",
    'cnLevels' : [0.01,0.05,0.1,0.25,0.5,0.75,1,1.25,1.5,2.0,3,4,5,7,10],
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     'lbTitleString'      : "[inch]",
     '_valid'    : ' %s Hour Period Ending at %s' % (hours,
        ts.localtime().strftime("%d %B %Y %I:%M %p %Z"),),
     '_title'    : "NMQ Q2 %s Hour Precipitation" % (hours,),
    }

    # Scale factor is 10
    routes = "c"
    if ts.minute == 0:
        routes = "ac"
    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 254.0, cfg)
    pqstr = "plot %s %s iowa_q2_%sh.png q2/iowa_q2_%sh_%s00.png png" % (
            routes, ts.strftime("%Y%m%d%H%M"), hours, hours, 
            ts.strftime("%H"))
    thumbpqstr = "plot c 000000000000 iowa_q2_%sh_thumb.png bogus png" % (
                hours,)
    iemplot.postprocess(tmpfp, pqstr, thumb=True, thumbpqstr=thumbpqstr)
    
    
    
if __name__ == "__main__":
    if len(sys.argv) == 7:
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5])),
                                   int(sys.argv[6]))
    else:
        doit( mx.DateTime.gmtime(), int(sys.argv[1]) )