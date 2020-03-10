"""Create a plot of the X Hour interval precipitation"""
import os
import sys
import datetime
import gzip
import tempfile

import numpy as np
import pytz
import pygrib
from pyiem.datatypes import distance
import pyiem.mrms as mrms
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import utc, logger

LOG = logger()
TMP = "/mesonet/tmp"


def doit(ts, hours):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at 1 AM
    ts = ts.replace(minute=0, second=0, microsecond=0)
    now = ts - datetime.timedelta(hours=hours - 1)
    interval = datetime.timedelta(hours=1)
    ets = datetime.datetime.utcnow()
    ets = ets.replace(tzinfo=pytz.utc)
    total = None
    while now < ets:
        gmt = now.astimezone(pytz.utc)
        gribfn = None
        for prefix in ["GaugeCorr", "RadarOnly"]:
            gribfn = mrms.fetch(prefix + "_QPE_01H", gmt)
            if gribfn is None:
                continue
            break
        if gribfn is None:
            LOG.info("%s MISSING %s", hours, now)
            now += interval
            continue
        fp = gzip.GzipFile(gribfn, "rb")
        (tmpfp, tmpfn) = tempfile.mkstemp()
        tmpfp = open(tmpfn, "wb")
        tmpfp.write(fp.read())
        tmpfp.close()
        grbs = pygrib.open(tmpfn)
        grb = grbs[1]
        os.unlink(tmpfn)
        # careful here, how we deal with the two missing values!
        if total is None:
            total = grb["values"]
        else:
            maxgrid = np.maximum(grb["values"], total)
            total = np.where(
                np.logical_and(grb["values"] >= 0, total >= 0),
                grb["values"] + total,
                maxgrid,
            )
        now += interval
        os.unlink(gribfn)

    if total is None:
        LOG.info("no data ts: %s hours: %s", ts, hours)
        return

    # Scale factor is 10
    routes = "c"
    if ts.minute == 0:
        routes = "ac"
    pqstr = "plot %s %s iowa_q2_%sh.png q2/iowa_q2_%sh_%s00.png png" % (
        routes,
        ts.strftime("%Y%m%d%H%M"),
        hours,
        hours,
        ts.strftime("%H"),
    )

    lts = ts.astimezone(pytz.timezone("America/Chicago"))
    subtitle = "Total up to %s" % (lts.strftime("%d %B %Y %I:%M %p %Z"),)
    mp = MapPlot(
        title=("NCEP MRMS Q3 (RADAR Only) %s Hour " "Precipitation [inch]")
        % (hours,),
        subtitle=subtitle,
    )

    clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]

    mp.contourf(
        mrms.XAXIS,
        mrms.YAXIS,
        distance(np.flipud(total), "MM").value("IN"),
        clevs,
        cmap=nwsprecip(),
    )
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr, view=False)
    mp.close()


def main(argv):
    """Go main"""
    if len(argv) == 7:
        ts = utc(
            int(argv[1]),
            int(argv[2]),
            int(argv[3]),
            int(argv[4]),
            int(argv[5]),
        )
        doit(ts, int(sys.argv[6]))
    else:
        ts = utc()
        try:
            doit(ts, int(argv[1]))
        except Exception as exp:
            LOG.info("failure ts: %s argv: %s", ts, argv[1])
            LOG.exception(exp)


if __name__ == "__main__":
    main(sys.argv)
