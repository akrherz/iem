"""Precip estimates"""
import datetime
import os

import numpy as np
import netCDF4
from pyiem import iemre, util
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
SRCDICT = {'mrms': 'NOAA MRMS (since 1 Jan 2014)',
           'prism': 'OSU PRISM (since 1 Jan 1981)'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = False
    desc['description'] = """This application allows the plotting of precipitation
    estimates from either MRMS or PRISM.  Please note that the start and
    end dates are inclusive.  The PRISM data is credit:
    <a href='http://prism.oregonstate.edu'>PRISM Climate Group</a>,
    Oregon State University, created 4 Feb 2004.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc['arguments'] = [
        dict(type='select', name='sector', default='IA',
             label='Select Sector:', options=PDICT),
        dict(type='select', name='src', default='mrms',
             label='Select Source:', options=SRCDICT),
        dict(type='select', name='ptype', default='c',
             label='Select Plot Type:', options=PDICT2),
        dict(type='date', name='sdate',
             default=today.strftime("%Y/%m/%d"),
             label='Start Date:', min="1981/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date:', min="1981/01/01"),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    from pyiem.plot import MapPlot, nwsprecip
    ctx = util.get_autoplot_context(fdict, get_description())
    ptype = ctx['ptype']
    sdate = ctx['sdate']
    edate = ctx['edate']
    src = ctx['src']
    if sdate.year != edate.year:
        raise Exception('Sorry, do not support multi-year plots yet!')
    days = (edate - sdate).days
    sector = ctx['sector']

    idx0 = iemre.daily_offset(sdate)
    idx1 = iemre.daily_offset(edate) + 1
    if src == 'mrms':
        ncfn = "/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (sdate.year, )
        ncvar = 'p01d'
        source = 'NOAA MRMS Q3'
        subtitle = 'NOAA MRMS Project, GaugeCorr and RadarOnly'
    else:
        ncfn = "/mesonet/data/prism/%s_daily.nc" % (sdate.year,)
        ncvar = 'ppt'
        source = 'OSU PRISM'
        subtitle = ('PRISM Climate Group, Oregon State Univ., '
                    'http://prism.oregonstate.edu, created 4 Feb 2004.')
    if not os.path.isfile(ncfn):
        raise Exception("No data for that year, sorry.")
    nc = netCDF4.Dataset(ncfn, 'r')
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
    if (idx1 - idx0) < 32:
        p01d = distance(np.sum(nc.variables[ncvar][idx0:idx1, :, :], 0),
                        'MM').value('IN')
    else:
        # Too much data can overwhelm this app, need to chunk it
        for i in range(idx0, idx1, 10):
            i2 = min([i+10, idx1])
            if idx0 == i:
                p01d = distance(np.sum(nc.variables[ncvar][i:i2, :, :], 0),
                                'MM').value('IN')
            else:
                p01d += distance(np.sum(nc.variables[ncvar][i:i2, :, :], 0),
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
                title='%s:: %s Total Precip' % (source, title),
                subtitle='Data from %s' % (subtitle,)
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


if __name__ == '__main__':
    plotter(dict())
