"""Plot monthly MRMS"""

import datetime
import sys

import numpy as np
from pyiem import iemre
from pyiem.plot import MapPlot
from pyiem.util import mm2inch, ncopen


def do_month(year, month, routes):
    """Generate a MRMS plot for the month!"""

    sts = datetime.datetime(year, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    ets = min(datetime.datetime.now(), ets)

    idx0 = iemre.daily_offset(sts)
    idx1 = iemre.daily_offset(ets)

    with ncopen(iemre.get_daily_mrms_ncname(year), "r") as nc:
        lats = nc.variables["lat"][:]
        lons = nc.variables["lon"][:]
        p01d = mm2inch(np.sum(nc.variables["p01d"][idx0:idx1, :, :], 0))

    dd = (ets - datetime.timedelta(days=1)).strftime("%-d %b %Y")
    mp = MapPlot(
        sector="iowa",
        title=f"MRMS {sts:%-d %b} - {dd} Total Precipitation",
        subtitle="Data from NOAA MRMS Project",
    )
    x, y = np.meshgrid(lons, lats)
    bins = [0.01, 0.1, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20]
    mp.pcolormesh(x, y, p01d, bins, units="inches")
    mp.drawcounties()
    currentfn = "summary/iowa_mrms_q3_month.png"
    archivefn = sts.strftime("%Y/%m/summary/iowa_mrms_q3_month.png")
    pqstr = f"plot {routes} {sts:%Y%m%d%H}00 {currentfn} {archivefn} png"
    mp.postprocess(pqstr=pqstr)


def main(argv):
    """Go Main Go"""
    if len(argv) == 3:
        do_month(int(argv[1]), int(argv[2]), "m")
    else:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        do_month(yesterday.year, yesterday.month, "cm")


if __name__ == "__main__":
    main(sys.argv)
