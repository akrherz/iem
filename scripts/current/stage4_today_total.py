"""
Create a plot of today's total precipitation from the Stage4 estimates
"""

import pygrib
import mx.DateTime
import iemplot
import numpy
import os, sys

def doday(ts):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    sts = ts + mx.DateTime.RelativeDateTime(hour=1)
    ets = ts + mx.DateTime.RelativeDateTime(hour=1, days=1)
    interval = mx.DateTime.RelativeDateTime(hours=1)
    now = sts
    total = None
    lts = None
    while now < ets:
        fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib" % (
            now.gmtime().strftime("%Y/%m/%d"), 
            now.gmtime().strftime("%Y%m%d%H") )
        if os.path.isfile(fp):
            lts = now
            grbs = pygrib.open(fp)

            if total is None:
                g = grbs[1]
                total = g["values"]
                lats, lons = g.latlons()
            else:
                total += grbs[1]["values"]
            grbs.close()
        now += interval
        
    # Now we dance
    cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     'lbTitleString'      : "[inch]",
     '_valid'    : 'Total up to %s' % (lts.strftime("%d %B %Y %I %p %Z"),),
     '_title'    : "NCEP StageIV Today's Precipitation [inch]",
    }

    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 25.4, cfg)
    pqstr = "plot ac %s00 iowa_stage4_1d.png iowa_stage4_1d.png png" % (
            ts.strftime("%Y%m%d%H"), )
    iemplot.postprocess(tmpfp, pqstr)
    
    # Midwest
    cfg['_midwest'] = True
    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 25.4, cfg)
    pqstr = "plot ac %s00 midwest_stage4_1d.png midwest_stage4_1d.png png" % (
            ts.strftime("%Y%m%d%H"), )
    iemplot.postprocess(tmpfp, pqstr)
    del(cfg['_midwest'])
    
    # CONUS
    cfg['_conus'] = True
    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 25.4, cfg)
    pqstr = "plot ac %s00 conus_stage4_1d.png conus_stage4_1d.png png" % (
            ts.strftime("%Y%m%d%H"), )
    iemplot.postprocess(tmpfp, pqstr)
    del(cfg['_conus'])
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        doday(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
    else:
        doday(mx.DateTime.now())