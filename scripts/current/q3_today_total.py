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

from pyiem.plot import MapPlot

def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at 1 AM
    now = ts.replace(hour=1, minute=0)
    ets = now + datetime.timedelta(hours=24)
    interval = datetime.timedelta(hours=1)

    precip = np.zeros( (3500,7000) )
    lastts = None
    while now < ets:
        gmt = now.astimezone(pytz.timezone("UTC"))
        # Only need tile 1 and 2 to sufficiently do Iowa
        for tile in range(1,3):
            fn = util.get_fn('1hrad', gmt, tile)
            if os.path.isfile(fn):
                lastts = now
                tilemeta, val = util.reader(fn)
                ysz, xsz = np.shape(val)
                if tile == 1:
                    x0 = 0
                    y0 = 1750
                if tile == 2:
                    x0 = 3500
                    y0 = 1750
                precip[y0:(y0+ysz),x0:(x0+xsz)] += val
        now += interval
    if lastts is None:
        print 'No MRMS Q3 Data found for date: %s' % (now.strftime("%d %B %Y"),)
        return
    lastts = lastts - datetime.timedelta(minutes=1)
    subtitle = "Total between 12:00 AM and %s" % (
                                            lastts.strftime("%I:%M %p %Z"),)
    routes = 'ac'
    if not realtime:
        routes = 'a'
    pqstr = "plot %s %s00 iowa_q2_1d.png iowa_q2_1d.png png" % (routes,
            ts.strftime("%Y%m%d%H"), )
    m = MapPlot(title="%s NMQ Q3 Today's Precipitation" % (
                                                    ts.strftime("%-d %b %Y"),),
                subtitle=subtitle)
        
    clevs = np.arange(0,0.2,0.05)
    clevs = np.append(clevs, np.arange(0.2, 1.0, 0.1))
    clevs = np.append(clevs, np.arange(1.0, 5.0, 0.25))
    clevs = np.append(clevs, np.arange(5.0, 10.0, 1.0))
    clevs[0] = 0.01

    x,y = np.meshgrid(util.XAXIS, util.YAXIS)
    m.pcolormesh(x, y, precip / 24.5, clevs, units='inch')

    #map.drawstates(zorder=2)
    m.drawcounties()
    m.postprocess(pqstr=pqstr)    
    
if __name__ == "__main__":
    ''' This is how we roll '''
    if len(sys.argv) == 4:
        date = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), 
                                 int(sys.argv[3]), 12, 0)
        realtime = False
    else:
        date = datetime.datetime.now()
        date = date - datetime.timedelta(minutes=60)
        date = date.replace(hour=12, minute=0, second=0, microsecond=0)
        realtime = True
    # Stupid pytz timezone dance
    date = date.replace(tzinfo=pytz.timezone("UTC"))
    date = date.astimezone(pytz.timezone("America/Chicago"))
    doday(date, realtime)
