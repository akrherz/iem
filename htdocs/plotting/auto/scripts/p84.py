import numpy as np
from pyiem import iemre, util
import datetime
import netCDF4
import os
from pyiem.datatypes import distance
from collections import OrderedDict

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
    ('WI', 'Wisconsin'),
    ('midwest', 'Mid West US')])
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
        dict(type='select', name='sector', default='IA',
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
    from pyiem.plot import MapPlot, nwsprecip
    ctx = util.get_autoplot_context(fdict, get_description())
    ptype = ctx['ptype']
    sdate = ctx['sdate']
    edate = ctx['edate']
    if sdate.year != edate.year:
        return 'Sorry, do not support multi-year plots yet!'
    days = (edate - sdate).days
    sector = ctx['sector']

    idx0 = iemre.daily_offset(sdate)
    idx1 = iemre.daily_offset(edate) + 1
    ncfn = "/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (sdate.year, )
    if not os.path.isfile(ncfn):
        return "No MRMS data for that year, sorry."
    nc = netCDF4.Dataset(ncfn, 'r')
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
    if sector == 'midwest':
        state = None
    else:
        state = sector
        sector = 'state'
    m = MapPlot(sector=sector, state=state, axisbg='white', nocaption=True,
                title='NOAA MRMS Q3:: %s Total Precip' % (title,),
                subtitle='Data from NOAA MRMS Project, GaugeCorr and RadarOnly'
                )
    if np.ma.is_masked(np.max(p01d)):
        return 'Data Unavailable'
    clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
    if days > 6:
        clevs = [0.01, 0.3, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20]
    if days > 29:
        clevs = [0.01, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30, 35]
    if days > 90:
        clevs = [0.01, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30, 35, 40]
    x, y = np.meshgrid(lons, lats)
    cmap = nwsprecip()
    cmap.set_over('k')
    if ptype == 'c':
        m.contourf(x, y, p01d, clevs, cmap=cmap, label='inches')
    else:
        m.pcolormesh(x, y, p01d, clevs, cmap=cmap, label='inches')
    if sector != 'midwest':
        m.drawcounties()
        m.drawcities()

    return m.fig
