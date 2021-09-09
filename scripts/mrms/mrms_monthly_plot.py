"""Plot monthly MRMS"""
import datetime
import sys

import numpy as np
from pyiem.plot import MapPlot
from pyiem.util import ncopen, mm2inch
from pyiem import iemre


def do_month(year, month, routes):
    """Generate a MRMS plot for the month!"""

    sts = datetime.datetime(year, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    today = datetime.datetime.now()
    if ets > today:
        ets = today

    idx0 = iemre.daily_offset(sts)
    idx1 = iemre.daily_offset(ets)

    nc = ncopen(iemre.get_daily_mrms_ncname(year), "r")

    lats = nc.variables["lat"][:]
    lons = nc.variables["lon"][:]
    p01d = mm2inch(np.sum(nc.variables["p01d"][idx0:idx1, :, :], 0))
    nc.close()

    mp = MapPlot(
        sector="iowa",
        title="MRMS %s - %s Total Precipitation"
        % (
            sts.strftime("%-d %b"),
            (ets - datetime.timedelta(days=1)).strftime("%-d %b %Y"),
        ),
        subtitle="Data from NOAA MRMS Project",
    )
    x, y = np.meshgrid(lons, lats)
    bins = [0.01, 0.1, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20]
    mp.pcolormesh(x, y, p01d, bins, units="inches")
    mp.drawcounties()
    currentfn = "summary/iowa_mrms_q3_month.png"
    archivefn = sts.strftime("%Y/%m/summary/iowa_mrms_q3_month.png")
    pqstr = "plot %s %s00 %s %s png" % (
        routes,
        sts.strftime("%Y%m%d%H"),
        currentfn,
        archivefn,
    )
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
