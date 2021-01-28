"""
 Create a plot of today's IFC estimated precip
"""
import datetime
import sys

import numpy as np
from pyiem.iemre import daily_offset
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import ncopen, mm2inch


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    idx = daily_offset(ts)
    with ncopen(
        f"/mesonet/data/iemre/{ts.year}_ifc_daily.nc", timeout=300
    ) as nc:
        xaxis = nc.variables["lon"][:]
        yaxis = nc.variables["lat"][:]
        total = nc.variables["p01d"][idx, :, :]
    lastts = datetime.datetime(ts.year, ts.month, ts.day, 23, 59)
    if realtime:
        now = datetime.datetime.now() - datetime.timedelta(minutes=60)
        lastts = now.replace(minute=59)
    subtitle = "Total between 12:00 AM and %s" % (lastts.strftime("%I:%M %p"),)
    routes = "ac"
    if not realtime:
        routes = "a"

    clevs = [
        0.01,
        0.1,
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        2.5,
        3,
        3.5,
        4,
        5,
        6,
        8,
        10,
    ]

    pqstr = ("plot %s %s00 iowa_ifc_1d.png iowa_ifc_1d.png png") % (
        routes,
        ts.strftime("%Y%m%d%H"),
    )
    mp = MapPlot(
        title=("%s Iowa Flood Center Today's Precipitation")
        % (ts.strftime("%-d %b %Y"),),
        subtitle=subtitle,
        sector="custom",
        west=xaxis[0],
        east=xaxis[-1],
        south=yaxis[0],
        north=yaxis[-1],
    )

    (lons, lats) = np.meshgrid(xaxis, yaxis)

    mp.pcolormesh(
        lons, lats, mm2inch(total), clevs, cmap=nwsprecip(), units="inch"
    )
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr, view=False)
    mp.close()


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        date = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
        realtime = False
    else:
        date = datetime.datetime.now() - datetime.timedelta(minutes=60)
        date = date.date()
        realtime = True
    doday(date, realtime)


if __name__ == "__main__":
    main(sys.argv)
