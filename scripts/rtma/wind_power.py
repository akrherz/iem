"""
Generate a plot of current wind power potential

This would involve converting wind velocity to m/s, multiply it by 1.35 to
extrapolate to 80 m, cubing that value, and multiplying it by 0.002641
(using the common GE 1.5-MW extra-long extended model turbine) to show the
potential wind power generation in MW (without taking into account the
capacity factor).

"""
import pygrib
from pyiem.plot import MapPlot
import pytz
import datetime
import os
import numpy
import sys

levels = [0., 0.01, 0.1, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 7, 10,
          20, 30, 40, 50]


def run(ts, routes):
    """ Run for a given UTC timestamp """
    fn = ts.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/rtma/%H/"
                      "rtma.t%Hz.awp2p5f000.grib2"))
    if not os.path.isfile(fn):
        print 'wind_power.py missing', fn
        return

    grb = pygrib.open(fn)
    try:
        u = grb.select(name='10 metre U wind component')[0]
        v = grb.select(name='10 metre V wind component')[0]
    except:
        print('Missing u/v wind for wind_power.py\nFN: %s' % (fn,))
        return
    mag = (u['values']**2 + v['values']**2)**.5

    mag = (mag * 1.35)**3 * 0.002641
    # 0.002641

    lats, lons = u.latlons()
    lts = ts.astimezone(pytz.timezone("America/Chicago"))
    pqstr = ("plot %s %s00 midwest/rtma_wind_power.png "
             "midwest/rtma_wind_power_%s00.png png"
             ) % (routes, ts.strftime("%Y%m%d%H"), ts.strftime("%H"))
    m = MapPlot(sector='midwest',
                title=(r'Wind Power Potential :: '
                       '(speed_mps_10m * 1.35)$^3$ * 0.002641'),
                subtitle=('valid: %s based on NOAA Realtime '
                          'Mesoscale Analysis'
                          ) % (lts.strftime("%d %b %Y %I %p")))
    m.pcolormesh(lons, lats, mag, numpy.array(levels), units='MW')

    m.postprocess(pqstr=pqstr)


def main(argv):
    """Main()"""
    if len(sys.argv) == 5:
        now = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                                int(sys.argv[3]), int(sys.argv[4]))
        routes = "a"
    else:
        now = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        routes = "ac"
    now = now.replace(tzinfo=pytz.timezone("UTC"))

    run(now, routes)

if __name__ == '__main__':
    main(sys.argv)
