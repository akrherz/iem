"""
Create a plot of the X Hour interval precipitation
"""

import datetime
import numpy as np
import os
import sys
import pyiem.mrms as mrms
import pytz
import gzip
import pygrib
import tempfile

from pyiem.plot import MapPlot


def doit(ts, hours):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at 1 AM
    ts = ts.replace(minute=0, second=0, microsecond=0)
    now = ts - datetime.timedelta(hours=hours-1)
    interval = datetime.timedelta(hours=1)
    ets = datetime.datetime.utcnow()
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    total = None
    while now < ets:
        gmt = now.astimezone(pytz.timezone("UTC"))
        for prefix in ['GaugeCorr', 'RadarOnly']:
            gribfn = gmt.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/" +
                                   prefix + "_QPE_01H/" +
                                   prefix + "_QPE_01H_00.00_%Y%m%d-%H%M00"
                                   ".grib2.gz"))
            if os.path.isfile(gribfn):
                break
        if not os.path.isfile(gribfn):
            print("q3_Xhour.py MISSING %s" % (gribfn,))
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
        now += interval

    if total is None:
        print("q3_Xhour.py no data ts: %s hours: %s" % (ts, hours))
        return

    # Scale factor is 10
    routes = "c"
    if ts.minute == 0:
        routes = "ac"
    pqstr = "plot %s %s iowa_q2_%sh.png q2/iowa_q2_%sh_%s00.png png" % (
            routes, ts.strftime("%Y%m%d%H%M"), hours, hours,
            ts.strftime("%H"))

    lts = ts.astimezone(pytz.timezone("America/Chicago"))
    subtitle = 'Total up to %s' % (lts.strftime("%d %B %Y %I:%M %p %Z"),)
    m = MapPlot(title=("NCEP MRMS Q3 (RADAR Only) %s Hour "
                       "Precipitation [inch]") % (hours,),
                subtitle=subtitle)

    clevs = np.arange(0, 0.2, 0.05)
    clevs = np.append(clevs, np.arange(0.2, 1.0, 0.1))
    clevs = np.append(clevs, np.arange(1.0, 5.0, 0.25))
    clevs = np.append(clevs, np.arange(5.0, 10.0, 1.0))
    clevs[0] = 0.01

    m.contourf(mrms.XAXIS, mrms.YAXIS, np.flipud(total) / 24.5, clevs)
    m.drawcounties()
    m.postprocess(pqstr=pqstr)


def main():
    """Go main"""
    if len(sys.argv) == 7:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]),
                               int(sys.argv[4]), int(sys.argv[5]))
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts, int(sys.argv[6]))
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts, int(sys.argv[1]))


if __name__ == "__main__":
    main()
