"""
Create a plot of the X Hour interval precipitation
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


def doit(ts, hours):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at 1 AM
    ts = ts.replace(minute=0, second=0, microsecond=0)
    now  = ts - datetime.timedelta(hours=hours-1)
    interval = datetime.timedelta(hours=1)

    precip = np.zeros( (3500,7000) )
    while now <= ts:
        # Only need tile 1 and 2 to sufficiently do Iowa
        for tile in range(1,3):
            fn = util.get_fn('1hrad', now, tile)
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
                print 'Missing 1HRAD MRMS for q3_today_total', fn
        now += interval

    # Scale factor is 10
    routes = "c"
    if ts.minute == 0:
        routes = "ac"
    pqstr = "plot %s %s iowa_q2_%sh.png q2/iowa_q2_%sh_%s00.png png" % (
            routes, ts.strftime("%Y%m%d%H%M"), hours, hours, 
            ts.strftime("%H"))

    lts = ts.astimezone(pytz.timezone("America/Chicago"))
    subtitle = 'Total up to %s' % (lts.strftime("%d %B %Y %I:%M %p %Z"),)
    m = MapPlot(title="NMQ Q3 %s Hour Precipitation [inch]" % (hours,),
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
    if len(sys.argv) == 7:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), 
                               int(sys.argv[3]),
                               int(sys.argv[4]), int(sys.argv[5]))
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts, int(sys.argv[6]))
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit( ts, int(sys.argv[1]) )