"""
 Create a plot of today's IFC estimated precip
"""

import datetime
import numpy as np
import os
import sys
import pytz
import osgeo.gdal as gdal
from pyiem.datatypes import distance
import matplotlib
matplotlib.use('agg')
from pyiem.plot import MapPlot


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # Start at midnight
    now = ts.replace(hour=0, minute=0)
    ets = now + datetime.timedelta(hours=24)
    interval = datetime.timedelta(minutes=5)
    currenttime = datetime.datetime.utcnow()
    currenttime = currenttime.replace(tzinfo=pytz.timezone("UTC"))

    total = None
    lastts = None
    while now <= ets:
        gmt = now.astimezone(pytz.timezone("UTC"))
        if gmt > currenttime:
            break
        fn = gmt.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/"
                           "GIS/ifc/p05m_%Y%m%d%H%M.png"))
        if not os.path.isfile(fn):
            now += interval
            continue
        png = gdal.Open(fn, 0)
        data = np.flipud(png.ReadAsArray())  # units are mm per 5 minutes
        data = np.where(data > 254, 0, data) / 10.0
        if total is None:
            total = data
        else:
            total += data

        lastts = now

        now += interval
    if lastts is None:
        print(('No IFC Data found for date: %s'
               ) % (now.strftime("%d %B %Y"),))
        return
    lastts = lastts - datetime.timedelta(minutes=1)
    subtitle = "Total between 12:00 AM and %s" % (
                                            lastts.strftime("%I:%M %p %Z"),)
    routes = 'ac'
    if not realtime:
        routes = 'a'

    clevs = np.arange(0, 0.25, 0.05)
    clevs = np.append(clevs, np.arange(0.25, 3., 0.25))
    clevs = np.append(clevs, np.arange(3., 10.0, 1))
    clevs[0] = 0.01

    sector = 'iowa'
    pqstr = ("plot %s %s00 %s_ifc_1d.png %s_ifc_1d.png png"
             ) % (routes, ts.strftime("%Y%m%d%H"), sector, sector)
    m = MapPlot(title=("%s Iowa Flood Center Today's Precipitation"
                       ) % (ts.strftime("%-d %b %Y"),),
                subtitle=subtitle, sector=sector)

    xaxis = -97.154167 + np.arange(1741) * 0.004167
    yaxis = 40.133331 + np.arange(1057) * 0.004167
    (x, y) = np.meshgrid(xaxis, yaxis)

    m.pcolormesh(x, y, distance(total, 'MM').value("IN"), clevs, units='inch')
    m.drawcounties()
    m.postprocess(pqstr=pqstr, view=False)
    m.close()


def main():
    if len(sys.argv) == 4:
        date = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                                 int(sys.argv[3]), 12, 0)
        realtime = False
    else:
        date = datetime.datetime.now()
        date = date - datetime.timedelta(minutes=60)
        date = date.replace(hour=12, minute=0, second=0, microsecond=0)
        realtime = True
    # Stupid pytz timezone dance
    date = date.replace(tzinfo=pytz.timezone("UTC"))
    date = date.astimezone(pytz.timezone("America/Chicago"))
    doday(date, realtime)


if __name__ == "__main__":
    main()
