"""
Create a plot of today's total precipitation from the Stage4 estimates
"""

import pygrib
import mx.DateTime
import iemplot
import numpy
import os, sys

def doday():
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    sts = mx.DateTime.DateTime(2010,4,1,12)
    ets = mx.DateTime.DateTime(2010,9,22,12)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    total = None
    while now < ets:
        fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.24h.grib" % (
            now.strftime("%Y/%m/%d"), 
            now.strftime("%Y%m%d%H") )
        if os.path.isfile(fp):
            lts = now
            grbs = pygrib.open(fp)

            if total is None:
                g = grbs[1]
                total = numpy.where(g["values"] > 25.4, 1., 0.)
                lats, lons = g.latlons()
            else:
                total += numpy.where(grbs[1]["values"] > 25.4, 1., 0.)
            grbs.close()
        now += interval
        
    # Now we dance
    cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     '_midwest'             : True,
     'lbTitleString'      : "[days]",
     '_valid'    : 'Number of days between 1 Apr and %s' % (
        now.strftime("%d %B %Y"),),
     '_title'    : "NCEP StageIV 24 Hour Rainfall Over 1 inch",
    }


    
    # Midwest
    tmpfp = iemplot.simple_grid_fill(lons, lats, total, cfg)
    iemplot.makefeature(tmpfp)

    
if __name__ == "__main__":
    doday()