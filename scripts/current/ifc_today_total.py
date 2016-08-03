"""
 Create a plot of today's IFC estimated precip
"""

import datetime
import numpy as np
import sys
from pyiem.datatypes import distance
import netCDF4
from pyiem.iemre import daily_offset
import matplotlib
matplotlib.use('agg')
from pyiem.plot import MapPlot, nwsprecip  # NOPEP8


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_ifc_daily.nc" % (ts.year,))
    idx = daily_offset(ts)
    xaxis = nc.variables['lon'][:]
    yaxis = nc.variables['lat'][:]
    total = nc.variables['p01d'][idx, :, :]
    nc.close()
    lastts = datetime.datetime(ts.year, ts.month, ts.day, 23, 59)
    if realtime:
        now = datetime.datetime.now() - datetime.timedelta(minutes=60)
        lastts = now.replace(minute=59)
    subtitle = "Total between 12:00 AM and %s" % (
                                                  lastts.strftime("%I:%M %p"),)
    routes = 'ac'
    if not realtime:
        routes = 'a'

    clevs = [0.01, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8,
             10]

    pqstr = ("plot %s %s00 iowa_ifc_1d.png iowa_ifc_1d.png png"
             ) % (routes, ts.strftime("%Y%m%d%H"))
    m = MapPlot(title=("%s Iowa Flood Center Today's Precipitation"
                       ) % (ts.strftime("%-d %b %Y"),),
                subtitle=subtitle, sector='custom',
                west=xaxis[0], east=xaxis[-1],
                south=yaxis[0], north=yaxis[-1])

    (x, y) = np.meshgrid(xaxis, yaxis)

    m.pcolormesh(x, y, distance(total, 'MM').value("IN"), clevs,
                 cmap=nwsprecip(), units='inch')
    m.drawcounties()
    m.postprocess(pqstr=pqstr, view=False)
    m.close()


def main(argv):
    if len(argv) == 4:
        date = datetime.date(int(argv[1]), int(argv[2]),
                             int(argv[3]))
        realtime = False
    else:
        date = datetime.datetime.now() - datetime.timedelta(minutes=60)
        date = date.date()
        realtime = True
    doday(date, realtime)


if __name__ == "__main__":
    main(sys.argv)
