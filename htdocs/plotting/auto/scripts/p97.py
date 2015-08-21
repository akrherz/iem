import numpy as np
from pyiem import iemre
import datetime
import netCDF4

PDICT = {'iowa': 'Iowa',
         'midwest': 'Mid West US'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """Departure of Precipitation
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    d['arguments'] = [
        dict(type='select', name='sector', default='iowa',
             label='Plot Sector:', options=PDICT),
        dict(type='date', name='date1',
             default=(today -
                      datetime.timedelta(days=30)).strftime("%Y/%m/%d"),
             label='Start Date:', min="1893/01/01"),
        dict(type='date', name='date2',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (inclusive):', min="1893/01/01"),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    from mpl_toolkits.basemap import maskoceans
    import matplotlib.cm as cm

    sector = fdict.get('sector', 'iowa')
    date1 = datetime.datetime.strptime(fdict.get('date1', '2015-01-01'),
                                       '%Y-%m-%d')
    date2 = datetime.datetime.strptime(fdict.get('date2', '2015-02-01'),
                                       '%Y-%m-%d')

    offset1 = iemre.daily_offset(date1)
    offset2 = iemre.daily_offset(date2) + 1

    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (date1.year,
                                                                 ), 'r')
    p01d = nc.variables['p01d']

    ncc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
    cp01d = ncc.variables['p01d']

    diff = ((np.sum(p01d[offset1:offset2, :, :], 0) -
             np.sum(cp01d[offset1:offset2, :, :], 0))) / 24.5

    lons = nc.variables['lon'][:] + 0.125
    lats = nc.variables['lat'][:] + 0.125
    x, y = np.meshgrid(lons, lats)
    diff = maskoceans(x, y, diff)
    # extra = lons[-1] + (lons[-1] - lons[-2])
    # lons = np.concatenate([lons, [extra, ]])
    # extra = lats[-1] + (lats[-1] - lats[-2])
    # lats = np.concatenate([lats, [extra, ]])
    x, y = np.meshgrid(lons, lats)

    m = MapPlot(sector=sector, axisbg='white',
                title=('%s - %s Precipitation Departure [inch]'
                       ) % (date1.strftime("%d %b %Y"),
                            date2.strftime("%d %b %Y")),
                subtitle='%s vs 1950-2014 Climatology' % (date1.year,))
    rng = int(max([0 - np.min(diff), np.max(diff)]))
    cmap = cm.get_cmap('RdYlBu')
    cmap.set_bad('white')
    m.contourf(x, y, diff, np.linspace(0 - rng - 0.5, rng + 0.6, 10,
                                       dtype='i'),
               cmap=cmap, units='inch')
    if sector == 'iowa':
        m.drawcounties()
    nc.close()
    ncc.close()

    return m.fig
