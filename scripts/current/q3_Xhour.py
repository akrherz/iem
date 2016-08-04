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
import requests
from pyiem.datatypes import distance
from pyiem.plot import MapPlot, nwsprecip

TMP = "/mesonet/tmp"


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
        gribfn = None
        for prefix in ['GaugeCorr', 'RadarOnly']:
            fn = gmt.strftime((prefix + "_QPE_01H_00.00_%Y%m%d-%H%M00"
                               ".grib2.gz"))
            res = requests.get(gmt.strftime(
                    ("http://mtarchive.geol.iastate.edu/%Y/%m/%d/mrms/ncep/" +
                     prefix + "_QPE_01H/" + fn)), timeout=30)
            if res.status_code != 200:
                continue
            o = open(TMP + "/" + fn, 'wb')
            o.write(res.content)
            o.close()
            gribfn = "%s/%s" % (TMP, fn)
            break
        if gribfn is None:
            print("q3_Xhour.py[%s] MISSING %s" % (hours, now))
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
        os.unlink(gribfn)

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

    clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]

    m.contourf(mrms.XAXIS, mrms.YAXIS,
               distance(np.flipud(total), 'MM').value('IN'), clevs,
               cmap=nwsprecip())
    m.drawcounties()
    m.postprocess(pqstr=pqstr, view=False)
    m.close()


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
