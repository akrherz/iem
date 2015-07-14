import numpy as np
from pyiem import iemre
import datetime
import netCDF4

PDICT = {'rsds': 'Solar Radiation'}
PDICT2 = {'c': 'Contour Plot',
          'g': 'Grid Cell Mesh'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This map presents a daily IEM ReAnalysis variable
    of your choice.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    d['arguments'] = [
        dict(type='select', name='var', default='rsds',
             label='Select Plot Variable:', options=PDICT),
        dict(type='select', name='ptype', default='c',
             label='Select Plot Type:', options=PDICT2),
        dict(type='date', name='date',
             default=today.strftime("%Y/%m/%d"),
             label='Date:', min="1893/01/01"),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    ptype = fdict.get('ptype', 'c')
    date = datetime.datetime.strptime(fdict.get('date', '2015-01-01'),
                                      '%Y-%m-%d')
    varname = fdict.get('var', 'rsds')

    idx0 = iemre.daily_offset(date)
    nc = netCDF4.Dataset(("/mesonet/data/iemre/%s_mw_daily.nc"
                          ) % (date.year, ), 'r')
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
    if varname == 'rsds':
        # Value is in W m**-2, we want MJ
        data = nc.variables['rsds'][idx0, :, :] * 86400. / 1000000.
        units = 'MJ d-1'
    nc.close()

    title = date.strftime("%-d %B %Y")
    m = MapPlot(sector='midwest', axisbg='white', nocaption=True,
                title='IEM Reanalysis of %s for %s' % (PDICT.get(varname),
                                                       title),
                subtitle='Data derived from various NOAA datasets'
                )
    if np.ma.is_masked(np.max(data)):
        return 'Data Unavailable'
    clevs = np.arange(0, 37, 3.)
    clevs[0] = 0.01
    x, y = np.meshgrid(lons, lats)
    if ptype == 'c':
        m.contourf(x, y, data, clevs, units=units)
    else:
        m.pcolormesh(x, y, data, clevs, units=units)

    return m.fig
