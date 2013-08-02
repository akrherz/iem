"""
 Create a plot of today's estimated precipitation based on the Q3 data
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

def doday(ts):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at 1 AM
    now = ts.replace(hour=1, minute=0)
    interval = datetime.timedelta(hours=1)

    precip = np.zeros( (3500,7000) )
    while now < ts:
        gmt = now.astimezone(pytz.timezone("UTC"))
        # Only need tile 1 and 2 to sufficiently do Iowa
        for tile in range(1,3):
            fn = util.get_fn('1hrad', gmt, tile)
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
    
   
    subtitle = 'Total up to %s' % (ts.strftime("%d %B %Y %I:%M %p %Z"),)
    pqstr = "plot ac %s00 iowa_q2_1d.png iowa_q2_1d.png png" % (
            ts.strftime("%Y%m%d%H"), )
    m = MapPlot(title="NMQ Q3 Today's Precipitation [inch]",
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
    ''' This is how we roll '''
    if len(sys.argv) == 4:
        ts = datetime.datetime(int(sys.argv[1]), 
                                   int(sys.argv[2]), int(sys.argv[3]), 23, 55)
    else:
        ts = datetime.datetime.now()
    ts = pytz.timezone("America/Chicago").localize(ts)
    doday(ts)
