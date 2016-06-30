import numpy as np
from pyiem import iemre
import datetime
import netCDF4
from pyiem.datatypes import distance

PDICT = {'iowa': 'Iowa',
         'midwest': 'Midwest'}
PDICT2 = {'c': 'Contour Plot',
          'g': 'Grid Cell Mesh'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = False
    d['description'] = """This map summarizes MRMS precipitation over
    a period of your choice.  The start and end dates are inclusive.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    d['arguments'] = [
        dict(type='select', name='sector', default='iowa',
             label='Select Sector:', options=PDICT),
        dict(type='select', name='ptype', default='c',
             label='Select Plot Type:', options=PDICT2),
        dict(type='date', name='sdate',
             default=today.strftime("%Y/%m/%d"),
             label='Start Date:', min="2014/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date:', min="2014/01/01"),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot
    ptype = fdict.get('ptype', 'c')
    sdate = datetime.datetime.strptime(fdict.get('sdate', '2015-01-01'),
                                       '%Y-%m-%d')
    edate = datetime.datetime.strptime(fdict.get('edate', '2015-01-01'),
                                       '%Y-%m-%d')
    if sdate.year != edate.year:
        return 'Sorry, do not support multi-year plots yet!'
    days = (edate - sdate).days
    sector = fdict.get('sector', 'iowa')
    if PDICT.get(sector) is None:
        return

    idx0 = iemre.daily_offset(sdate)
    idx1 = iemre.daily_offset(edate) + 1
    nc = netCDF4.Dataset(("/mesonet/data/iemre/%s_mw_mrms_daily.nc"
                          ) % (sdate.year, ), 'r')
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
    if (idx1 - idx0) < 32:
        p01d = distance(np.sum(nc.variables['p01d'][idx0:idx1, :, :], 0),
                        'MM').value('IN')
    else:
        # Too much data can overwhelm this app, need to chunk it
        for i in range(idx0, idx1, 10):
            i2 = min([i+10, idx1])
            if idx0 == i:
                p01d = distance(np.sum(nc.variables['p01d'][i:i2, :, :], 0),
                                'MM').value('IN')
            else:
                p01d += distance(np.sum(nc.variables['p01d'][i:i2, :, :], 0),
                                 'MM').value('IN')
    nc.close()

    if sdate == edate:
        title = sdate.strftime("%-d %B %Y")
    else:
        title = "%s to %s (inclusive)" % (sdate.strftime("%-d %b %Y"),
                                          edate.strftime("%-d %b %Y"))
    m = MapPlot(sector=sector, axisbg='white', nocaption=True,
                title='NOAA MRMS Q3:: %s Total Precip' % (title,),
                subtitle='Data from NOAA MRMS Project, GaugeCorr and RadarOnly'
                )
    if np.ma.is_masked(np.max(p01d)):
        return 'Data Unavailable'
    clevs = np.arange(0, 0.25, 0.05)
    clevs = np.append(clevs, np.arange(0.25, 3., 0.25))
    clevs = np.append(clevs, np.arange(3., 10.0, 1))
    if days > 6:
        clevs = np.arange(0, 0.5, 0.1)
        clevs = np.append(clevs, np.arange(0.5, 6., 0.5))
        clevs = np.append(clevs, np.arange(6., 21.0, 2))
    if days > 29:
        clevs = np.arange(0, 1., 0.25)
        clevs = np.append(clevs, np.arange(1., 6., 1.))
        clevs = np.append(clevs, np.arange(6., 31.0, 1))
    if days > 90:
        clevs = np.arange(0, 2., 0.5)
        clevs = np.append(clevs, np.arange(2., 10., 2.))
        clevs = np.append(clevs, np.arange(10., 61.0, 5.))
    clevs[0] = 0.01
    x, y = np.meshgrid(lons, lats)
    if ptype == 'c':
        m.contourf(x, y, p01d, clevs, label='inches')
    else:
        m.pcolormesh(x, y, p01d, clevs, label='inches')
    if sector == 'iowa':
        m.drawcounties()
        m.drawcities()

    return m.fig
