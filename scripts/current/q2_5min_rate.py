"""
Create a plot of the 5 minute interval precip rate
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

def doit(ts):
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
    nc = netCDF3.Dataset(make_fp(ts))
    val = nc.variables["preciprate_hsr"][:]
    nc.close()
        
    # Put some bad values in just to make the plot happy
    val[10:20,10:20] = 100.0
    # Now we dance
    cfg = { 
    'cnLevelSelectionMode': "ExplicitLevels",
    'cnLevels' : [0.01,0.05,0.1,0.25,0.5,0.75,1,1.25,1.5,2.0,2.5,3,4],
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     'lbTitleString'      : "[inch/hr]",
     '_valid'    : 'Valid %s' % (
        ts.localtime().strftime("%d %B %Y %I:%M %p %Z"),),
     '_title'    : "NMQ Q2 Precipitation Rate [inch/hr]",
    }

    # Scale factor is 10
    tmpfp = iemplot.simple_grid_fill(lons, lats, val / 254.0, cfg)
    pqstr = "plot ac %s iowa_q2_5m.png q2/iowa_q2_5m_%s.png png" % (
            ts.strftime("%Y%m%d%H%M"), ts.strftime("%H%M"))
    iemplot.postprocess(tmpfp, pqstr)
    
    
    
if __name__ == "__main__":
    if len(sys.argv) == 6:
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5])))
    else:
        doit( mx.DateTime.gmtime() )