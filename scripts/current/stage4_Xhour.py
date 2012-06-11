"""
Create a variable X hour plot of stage IV estimates
"""

import pygrib
import mx.DateTime
import iemplot
import numpy
import os, sys

def do(ts, hours):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    sts = ts - mx.DateTime.RelativeDateTime(hours=hours, minute=0)
    ets = ts 
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
    
    if lts is None and ts.hour > 1:
        print 'Missing StageIV data!'
    if lts is None:
        return
    
    # Now we dance
    cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
      'cnLevelSelectionMode': "ExplicitLevels",
      'cnLevels' : [0.01,0.1,0.25,0.5,1,2,3,5,8,9.9],
     'lbTitleString'      : "[inch]",
     '_valid'    : 'Total up to %s' % (
        (lts - mx.DateTime.RelativeDateTime(minutes=1)).strftime("%d %B %Y %I:%M %p %Z"),),
     '_title'    : "NCEP StageIV %s Hour Precipitation [inch]" % (hours,),
    }

    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 25.4, cfg)
    pqstr = "plot ac %s00 iowa_stage4_%sh.png iowa_stage4_%sh.png png" % (
            ts.strftime("%Y%m%d%H"), hours, hours)
    iemplot.postprocess(tmpfp, pqstr)
    
    # Midwest
    cfg['_midwest'] = True
    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 25.4, cfg)
    pqstr = "plot ac %s00 midwest_stage4_%sh.png midwest_stage4_%sh.png png" % (
            ts.strftime("%Y%m%d%H"), hours, hours)
    iemplot.postprocess(tmpfp, pqstr)
    del(cfg['_midwest'])
    
    # CONUS
    cfg['_conus'] = True
    tmpfp = iemplot.simple_grid_fill(lons, lats, total / 25.4, cfg)
    pqstr = "plot ac %s00 conus_stage4_%sh.png conus_stage4_%sh.png png" % (
            ts.strftime("%Y%m%d%H"), hours, hours)
    iemplot.postprocess(tmpfp, pqstr)
    del(cfg['_conus'])
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        do(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])),
              int(sys.argv[4]))
    else:
        do(mx.DateTime.now(), int(sys.argv[1]))