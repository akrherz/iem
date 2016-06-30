"""
Create a variable X hour plot of stage IV estimates
"""

import pygrib
import datetime
import pytz
from pyiem.datatypes import distance
from pyiem.plot import MapPlot
import os
import sys
import matplotlib.cm as cm


def do(ts, hours):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    ts = ts.replace(minute=0)
    sts = ts - datetime.timedelta(hours=hours)
    ets = ts
    interval = datetime.timedelta(hours=1)
    now = sts
    total = None
    lts = None
    while now < ets:
        fn = ("/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib"
              ) % (now.strftime("%Y/%m/%d"), now.strftime("%Y%m%d%H"))

        if os.path.isfile(fn):
            lts = now
            grbs = pygrib.open(fn)

            if total is None:
                g = grbs[1]
                total = g["values"].filled(0)
                lats, lons = g.latlons()
            else:
                total += grbs[1]["values"].filled(0)
            grbs.close()
        now += interval

    if lts is None and ts.hour > 1:
        print 'Missing StageIV data!'
    if lts is None:
        return

    cmap = cm.get_cmap("jet")
    cmap.set_under('white')
    cmap.set_over('black')
    clevs = [0.01, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 9.9]
    localtime = (ts - datetime.timedelta(minutes=1)).astimezone(
                                        pytz.timezone("America/Chicago"))

    for sector in ['iowa', 'midwest', 'conus']:
        m = MapPlot(sector=sector,
                    title='NCEP Stage IV %s Hour Precipitation' % (hours,),
                    subtitle='Total up to %s' % (
                                    localtime.strftime("%d %B %Y %I %p %Z"),))
        m.pcolormesh(lons, lats, distance(total, 'MM').value('IN'), clevs,
                     units='inch')
        pqstr = "plot %s %s00 %s_stage4_%sh.png %s_stage4_%sh_%s.png png" % (
                                'ac', ts.strftime("%Y%m%d%H"), sector, hours,
                                sector, hours, ts.strftime("%H"))
        if sector == 'iowa':
            m.drawcounties()
        m.postprocess(pqstr=pqstr)
        m.close()


def main():
    if len(sys.argv) == 4:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), int(sys.argv[4]))
        hr = int(sys.argv[5])
    else:
        ts = datetime.datetime.utcnow()
        hr = int(sys.argv[1])
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    do(ts, hr)

if __name__ == "__main__":
    main()
