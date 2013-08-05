"""
Generate a plot of recent rainfall rate
"""

import datetime
import numpy as np
import os
import sys
sys.path.insert(0, '../mrms')
import util
import pytz
import gzip

from iem.plot import MapPlot

def doit(ts, routes):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Mod the minute down
    remain = ts.minute % 2
    now = ts - datetime.timedelta(minutes=remain+4)
    
    precip = np.zeros( (3500,7000) )
    for tile in range(1,3):
        fn = util.get_fn('rainrate', now, tile)
        if os.path.isfile(fn):
            tilemeta, val = util.reader(fn)
            ysz, xsz = np.shape(val)
            if tile == 1:
                x0 = 0
                y0 = 1750
            if tile == 2:
                x0 = 3500
                y0 = 1750
            precip[y0:(y0+ysz),x0:(x0+xsz)] += val
        else:
            print 'Missing RAINRATE MRMS for q3_today_total', fn
    
    lts = now.astimezone(pytz.timezone("America/Chicago"))

    subtitle = 'Rate at %s' % (lts.strftime("%d %B %Y %I:%M %p %Z"),)
    pqstr = "plot %s %s iowa_q2_5m.png q2/iowa_q2_5m_%s.png png" % (routes,
            ts.strftime("%Y%m%d%H%M"), ts.strftime("%H%M"))
    m = MapPlot(title="NMQ Q3 Precipitation Rate [inch/hr]",
                subtitle=subtitle, pqstr=pqstr)
        
    clevs = np.arange(0,0.2,0.05)
    clevs = np.append(clevs, np.arange(0.2, 1.0, 0.1))
    clevs = np.append(clevs, np.arange(1.0, 5.0, 0.25))
    clevs = np.append(clevs, np.arange(5.0, 10.0, 1.0))
    clevs[0] = 0.01

    m.contourf(util.XAXIS, util.YAXIS, precip / 24.5, clevs)

    #map.drawstates(zorder=2)
    m.drawcounties()
    m.postprocess()   
    
    
    
if __name__ == "__main__":
    if len(sys.argv) == 6:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), 
                               int(sys.argv[3]),
                               int(sys.argv[4]), int(sys.argv[5]))
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts , 'a')
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit( ts , 'ac')