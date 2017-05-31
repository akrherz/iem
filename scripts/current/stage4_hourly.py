"""
    Plot the hourly stage IV precip data 
"""
import sys
import os
from pyiem.plot import MapPlot
import pygrib
import datetime
import pytz
import matplotlib.cm as cm

gmtnow = datetime.datetime.utcnow()
gmtnow = gmtnow.replace(tzinfo=pytz.timezone("UTC"))


def doit(ts):
    """
    Generate hourly plot of stage4 data
    """
    routes = "a"
    if ((gmtnow - ts).days * 86400. + (gmtnow - ts).seconds) < 7200:
        routes = "ac"

    fn = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib" % (
                        ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H") )
    if not os.path.isfile(fn):
        print 'current/stage4_hourly.py Missing stage4 %s' % (fn,)
        return

    grbs = pygrib.open(fn)
    grib = grbs[1]
    lats, lons = grib.latlons()
    vals = grib.values / 25.4

    cmap = cm.get_cmap("jet")
    cmap.set_under('white')
    cmap.set_over('black')
    clevs = [0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.5,2,3]
    localtime = ts.astimezone(pytz.timezone("America/Chicago"))

    for sector in ['iowa', 'midwest', 'conus']:
        m = MapPlot(sector=sector,
                    title='Stage IV One Hour Precipitation',
                    subtitle='Hour Ending %s' % (
                                    localtime.strftime("%d %B %Y %I %p %Z"),))
        m.pcolormesh(lons, lats, vals, clevs, units='inch')
        pqstr = "plot %s %s00 %s_stage4_1h.png %s_stage4_1h_%s.png png" % (
                                routes, ts.strftime("%Y%m%d%H"), sector,
                                sector, ts.strftime("%H"))
        if sector == 'iowa':
            m.drawcounties()
        m.postprocess(view=False, pqstr=pqstr)
        m.close()


def main():
    """Go main Go"""
    if len(sys.argv) == 5:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), int(sys.argv[4]))
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts)
    else:
        ts = datetime.datetime.utcnow()
        ts = ts.replace(tzinfo=pytz.timezone("UTC"))
        doit(ts)
        doit(ts - datetime.timedelta(hours=24))
        doit(ts - datetime.timedelta(hours=48))


if __name__ == '__main__':
    main()
