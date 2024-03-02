"""
Generate a plot of current wind power potential

This would involve converting wind velocity to m/s, multiply it by 1.35 to
extrapolate to 80 m, cubing that value, and multiplying it by 0.002641
(using the common GE 1.5-MW extra-long extended model turbine) to show the
potential wind power generation in MW (without taking into account the
capacity factor).

RUN from RUN_40_AFTER.sh

"""

import datetime
import os
import sys
import time
from zoneinfo import ZoneInfo

import numpy as np
import pygrib
from pyiem.plot import MapPlot
from pyiem.util import logger, utc

LOG = logger()
LEVELS = [
    0.0,
    0.01,
    0.1,
    0.25,
    0.5,
    0.75,
    1,
    1.25,
    1.5,
    2,
    2.5,
    3,
    4,
    5,
    7,
    10,
    20,
    30,
    40,
    50,
]


def run(ts, routes):
    """Run for a given UTC timestamp"""
    fn = ts.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/rtma/%H/"
        "rtma.t%Hz.awp2p5f000.grib2"
    )
    if not os.path.isfile(fn):
        LOG.info("File Not Found: %s", fn)
        return

    grb = pygrib.open(fn)
    try:
        u = grb.select(name="10 metre U wind component")[0]
        v = grb.select(name="10 metre V wind component")[0]
    except Exception as exp:
        LOG.info("Missing u/v wind for wind_power.py\nFN: %s\n%s", fn, exp)
        return
    mag = np.hypot(u["values"], v["values"])

    mag = (mag * 1.35) ** 3 * 0.002641
    # 0.002641

    lats, lons = u.latlons()
    lts = ts.astimezone(ZoneInfo("America/Chicago"))
    pqstr = (
        f"plot {routes} {ts:%Y%m%d%H}00 midwest/rtma_wind_power.png "
        f"midwest/rtma_wind_power_{ts:%H}00.png png"
    )
    mp = MapPlot(
        sector="midwest",
        title=(
            "Wind Power Potential :: (speed_mps_10m * 1.35)$^3$ * 0.002641"
        ),
        subtitle=(
            f"valid: {lts:%d %b %Y %I %p} based on "
            "NOAA Realtime Mesoscale Analysis"
        ),
    )
    mp.pcolormesh(lons, lats, mag, np.array(LEVELS), units="MW")

    mp.postprocess(pqstr=pqstr)
    mp.close()


def main(argv):
    """Main()"""
    if len(sys.argv) == 5:
        now = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
        routes = "a"
    else:
        now = utc() - datetime.timedelta(hours=1)
        routes = "ac"
        # the 3z RTMA is always late, so we shall wait
        if now.hour == 3:
            time.sleep(60 * 10)

    run(now, routes)


if __name__ == "__main__":
    main(sys.argv)
