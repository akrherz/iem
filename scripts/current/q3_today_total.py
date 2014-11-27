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
import pygrib
import gzip
import tempfile

from pyiem.plot import MapPlot

def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at 1 AM
    now = ts.replace(hour=1, minute=0)
    ets = now + datetime.timedelta(hours=24)
    interval = datetime.timedelta(hours=1)
    currenttime = datetime.datetime.utcnow()
    currenttime = currenttime.replace(tzinfo=pytz.timezone("UTC"))

    total = None
    lastts = None
    while now < ets:
        gmt = now.astimezone(pytz.timezone("UTC"))
        if gmt > currenttime:
            break
        gribfn = gmt.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/"
                +"RadarOnly_QPE_01H/"
                +"RadarOnly_QPE_01H_00.00_%Y%m%d-%H%M00.grib2.gz"))
        if not os.path.isfile(gribfn):
            print("q3_today_total.py MISSING %s" % (gribfn,))
            now += interval
            continue
        fp = gzip.GzipFile(gribfn, 'rb')
        (tmpfp, tmpfn) = tempfile.mkstemp()
        tmpfp = open(tmpfn, 'wb')
        tmpfp.write(fp.read())
        tmpfp.close()
        grbs = pygrib.open(tmpfn)
        grb = grbs[1]
        os.unlink(tmpfn)
        # careful here, how we deal with the two missing values!
        if total is None:
            total = grb['values']
        else:
            maxgrid = np.maximum(grb['values'], total)
            total = np.where(np.logical_and(grb['values'] >= 0,
                                           total >= 0),
                             grb['values'] + total, maxgrid)


        lastts = now

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
    m = MapPlot(title="%s NCEP MRMS Q3 Today's Precipitation" % (
                                                    ts.strftime("%-d %b %Y"),),
                subtitle=subtitle)
        
    clevs = np.arange(0,0.2,0.05)
    clevs = np.append(clevs, np.arange(0.2, 1.0, 0.1))
    clevs = np.append(clevs, np.arange(1.0, 5.0, 0.25))
    clevs = np.append(clevs, np.arange(5.0, 10.0, 1.0))
    clevs[0] = 0.01

    x,y = np.meshgrid(util.XAXIS, util.YAXIS)
    m.pcolormesh(x, y, total / 24.5, clevs, units='inch')

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
