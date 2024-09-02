"""Create a plot of the X Hour interval precipitation.

Run from RUN_10_AFTER.sh for 1,3 and 6 hours ago
"""

import gzip
import os
import tempfile
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
import numpy as np
import pygrib
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
    now = ts - timedelta(hours=hours - 1)
    interval = timedelta(hours=1)
    ets = utc()
    total = None
    while now < ets:
        gmt = now.astimezone(ZoneInfo("UTC"))
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
        with (
            gzip.GzipFile(gribfn, "rb") as gzfp,
            tempfile.NamedTemporaryFile(delete=False) as fp,
        ):
            fp.write(gzfp.read())
        grbs = pygrib.open(fp.name)
        grb = grbs[1]
        grbs.close()
        os.unlink(fp.name)
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

    lts = ts.astimezone(ZoneInfo("America/Chicago"))
    subtitle = f"Total up to {lts:%d %B %Y %I:%M %p %Z}"
    mp = MapPlot(
        title=f"NCEP MRMS (RADAR Only) {hours} Hour Precipitation [inch]",
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


@click.command()
@click.option("--hours", type=int, default=1, help="Number of hours to accum")
@click.option("--valid", type=click.DateTime(), help="UTC Timestamp")
def main(hours: int, valid: datetime):
    """Go main"""
    valid = utc()
    if valid is not None:
        valid = valid.replace(tzinfo=ZoneInfo("UTC"))
    doit(valid, hours)


if __name__ == "__main__":
    main()
