"""Create a plot of the X Hour interval precipitation"""
import datetime
import gzip
import os
import sys
import tempfile

import numpy as np
import pygrib
import pytz
from pyiem import mrms
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import logger, mm2inch, utc

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
        for prefix in ["MultiSensor_QPE_01H_Pass2", "RadarOnly_QPE_01H"]:
            gribfn = mrms.fetch(prefix, gmt)
            if gribfn is None:
                continue
            break
        if gribfn is None:
            LOG.info("%s MISSING %s", hours, now)
            now += interval
            continue
        fp = gzip.GzipFile(gribfn, "rb")
        (tmpfp, tmpfn) = tempfile.mkstemp()
        with open(tmpfn, "wb") as tmpfp:
            tmpfp.write(fp.read())
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
    pqstr = (
        f"plot {routes} {ts:%Y%m%d%H%M} iowa_q2_{hours}h.png "
        f"q2/iowa_q2_{hours}h_{ts:%H}00.png png"
    )

    lts = ts.astimezone(pytz.timezone("America/Chicago"))
    subtitle = f"Total up to {lts:%d %B %Y %I:%M %p %Z}"
    mp = MapPlot(
        title=f"NCEP MRMS Q3 (RADAR Only) {hours} Hour Precipitation [inch]",
        subtitle=subtitle,
    )

    clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]

    x, y = np.meshgrid(mrms.XAXIS, mrms.YAXIS)
    mp.contourf(
        x,
        y,
        mm2inch(np.flipud(total)),
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
        doit(ts, int(argv[1]))


if __name__ == "__main__":
    main(sys.argv)
