import numpy as np
from pyiem import iemre
from pyiem.datatypes import temperature, speed
import datetime
import netCDF4
from collections import OrderedDict

PDICT = OrderedDict({'p01d_12z': '24 Hour Precipitation at 12 UTC',
                     'p01d': 'Calendar Day Precipitation',
                     'low_tmpk': 'Minimum Temperature',
                     'low_tmpk_12z': 'Minimum Temperature at 12 UTC',
                     'high_tmpk': 'Maximum Temperature',
                     'high_tmpk_12z': 'Maximum Temperature at 12 UTC',
                     'p01d': 'Calendar Day Precipitation',
                     'rsds': 'Solar Radiation',
                     'avg_dwpk': 'Average Dew Point',
                     'wind_speed': 'Average Wind Speed',
                     })
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
        data = nc.variables[varname][idx0, :, :] * 86400. / 1000000.
        units = 'MJ d-1'
        clevs = np.arange(0, 37, 3.)
        clevs[0] = 0.01
        clevstride = 1
    elif varname in ['wind_speed', ]:
        data = speed(nc.variables[varname][idx0, :, :], 'MPS').value('MPH')
        units = 'mph'
        clevs = np.arange(0, 41, 2)
        clevs[0] = 0.01
        clevstride = 2
    elif varname in ['p01d', 'p01d_12z']:
        # Value is in W m**-2, we want MJ
        data = nc.variables[varname][idx0, :, :] / 25.4
        units = 'inch'
        clevs = np.arange(0, 0.25, 0.05)
        clevs = np.append(clevs, np.arange(0.25, 3., 0.25))
        clevs = np.append(clevs, np.arange(3., 10.0, 1))
        clevs[0] = 0.01
        clevstride = 1
    elif varname in ['high_tmpk', 'low_tmpk', 'high_tmpk_12z', 'low_tmpk_12z',
                     'avg_dwpk']:
        # Value is in W m**-2, we want MJ
        data = temperature(nc.variables[varname][idx0, :, :], 'K').value('F')
        units = 'F'
        clevs = np.arange(-30, 120, 2)
        clevstride = 5
    nc.close()

    title = date.strftime("%-d %B %Y")
    m = MapPlot(sector='midwest', axisbg='white', nocaption=True,
                title='IEM Reanalysis of %s for %s' % (PDICT.get(varname),
                                                       title),
                subtitle='Data derived from various NOAA datasets'
                )
    if np.ma.is_masked(np.max(data)):
        return 'Data Unavailable'
    x, y = np.meshgrid(lons, lats)
    if ptype == 'c':
        m.contourf(x, y, data, clevs, clevstride=clevstride, units=units)
    else:
        m.pcolormesh(x, y, data, clevs, clevstride=clevstride, units=units)

    return m.fig
