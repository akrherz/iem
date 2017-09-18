"""Precip days to accumulate"""
import datetime
import os
from collections import OrderedDict

import numpy as np
import netCDF4
from pyiem import iemre, util
from pyiem.datatypes import distance

PDICT = OrderedDict([
    ('IA', 'Iowa'),
    ('IL', 'Illinois'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MO', 'Missouri'),
    ('NE', 'Nebraska'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('SD', 'South Dakota'),
    ('WI', 'Wisconsin')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = False
    desc['description'] = """This application will make a map with the number
    of days it takes to accumulate a given amount of precipitation.  This is
    based on progressing daily back in time for up to 90 days to accumulate
    the specified amount.  This plot will take some time to generate, so please
    be patient with it!
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc['arguments'] = [
        dict(type='select', name='sector', default='IA',
             label='Select Sector:', options=PDICT),
        dict(type='date', name='date',
             default=today.strftime("%Y/%m/%d"),
             label='Date:', min="2011/01/01"),
        dict(type='float', name='threshold', default=2.,
             label='Date Precipitation Threshold (inch)'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from pyiem.plot.geoplot import MapPlot

    ctx = util.get_autoplot_context(fdict, get_description())
    date = ctx['date']
    sector = ctx['sector']
    threshold = ctx['threshold']
    threshold_mm = distance(threshold, 'IN').value('MM')
    window_sts = date - datetime.timedelta(days=90)
    if window_sts.year != date.year:
        raise Exception('Sorry, do not support multi-year plots yet!')

    idx0 = iemre.daily_offset(window_sts)
    idx1 = iemre.daily_offset(date)
    ncfn = "/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (date.year, )
    ncvar = 'p01d'
    if not os.path.isfile(ncfn):
        raise Exception("No data for that year, sorry.")
    nc = netCDF4.Dataset(ncfn, 'r')

    grid = np.zeros((len(nc.dimensions['lat']),
                     len(nc.dimensions['lon'])))
    total = np.zeros((len(nc.dimensions['lat']),
                      len(nc.dimensions['lon'])))
    for i, idx in enumerate(range(idx1, idx1-90, -1)):
        total += nc.variables[ncvar][idx, :, :]
        grid = np.where(np.logical_and(grid == 0,
                                       total > threshold_mm), i, grid)
    lon = np.append(nc.variables['lon'][:], [-80.5])
    lat = np.append(nc.variables['lat'][:], [49.])
    nc.close()

    mp = MapPlot(sector='state', state=sector, titlefontsize=14,
                 subtitlefontsize=12,
                 title=("NOAA MRMS Q3: Number of Recent Days "
                        "till Accumulating %s\" of Precip"
                        ) % (threshold, ),
                 subtitle=("valid %s: based on per calendar day "
                           "estimated preciptation, GaugeCorr and "
                           "RadarOnly products"
                           ) % (date.strftime("%-d %b %Y"), ))
    x, y = np.meshgrid(lon, lat)
    cmap = plt.get_cmap('terrain')
    cmap.set_over('k')
    cmap.set_under('white')
    mp.pcolormesh(x, y, grid,
                  np.arange(0, 81, 10), cmap=cmap, units='days')
    mp.drawcounties()
    mp.drawcities()

    return mp.fig


if __name__ == '__main__':
    plotter(dict())
