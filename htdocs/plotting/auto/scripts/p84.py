"""Precip estimates"""
import datetime
import os
from collections import OrderedDict

import numpy as np
import netCDF4
from pyiem import iemre, util
from pyiem.datatypes import distance
from pyiem.reference import state_bounds

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
PDICT3 = {'acc': 'Accumulation',
          'dep': 'Departure from Average [inch]',
          'per': 'Percent of Average [%]'}
PDICT4 = {'yes': 'Yes, overlay Drought Monitor',
          'no': 'No, do not overlay Drought Monitor'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = False
    desc['description'] = """This application allows the plotting of precipitation
    estimates from either MRMS or PRISM.  Please note that the start and
    end dates are inclusive.  There is a three day delay for the arrival of the
    PRISM data. The PRISM data is credit:
    <a href='http://prism.oregonstate.edu'>PRISM Climate Group</a>,
    Oregon State University, created 4 Feb 2004.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc['arguments'] = [
        dict(type='select', name='sector', default='IA',
             label='Select Sector:', options=PDICT),
        dict(type='select', name='src', default='mrms',
             label='Select Source:', options=SRCDICT),
        dict(type='select', name='opt', default='acc',
             label='Plot Precipitation As:', options=PDICT3),
        dict(type='select', name='usdm', default='no',
             label='Overlay Drought Monitor', options=PDICT4),
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
    import matplotlib.pyplot as plt
    from pyiem.plot import MapPlot, nwsprecip
    ctx = util.get_autoplot_context(fdict, get_description())
    ptype = ctx['ptype']
    sdate = ctx['sdate']
    edate = ctx['edate']
    src = ctx['src']
    opt = ctx['opt']
    usdm = ctx['usdm']
    if sdate.year != edate.year:
        raise Exception('Sorry, do not support multi-year plots yet!')
    days = (edate - sdate).days
    sector = ctx['sector']

    if sdate == edate:
        title = sdate.strftime("%-d %B %Y")
    else:
        title = "%s to %s (inclusive)" % (sdate.strftime("%-d %b"),
                                          edate.strftime("%-d %b %Y"))
    x0 = 0
    x1 = -1
    y0 = 0
    y1 = -1
    if sector == 'midwest':
        state = None
    else:
        state = sector
        sector = 'state'

    if src == 'mrms':
        ncfn = "/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (sdate.year, )
        clncfn = "/mesonet/data/iemre/mw_mrms_dailyc.nc"
        ncvar = 'p01d'
        source = 'MRMS Q3'
        subtitle = 'NOAA MRMS Project, GaugeCorr and RadarOnly'
    else:
        ncfn = "/mesonet/data/prism/%s_daily.nc" % (sdate.year,)
        clncfn = "/mesonet/data/prism/prism_dailyc.nc"
        ncvar = 'ppt'
        source = 'OSU PRISM'
        subtitle = ('PRISM Climate Group, Oregon State Univ., '
                    'http://prism.oregonstate.edu, created 4 Feb 2004.')

    mp = MapPlot(sector=sector, state=state, axisbg='white', nocaption=True,
                 title='%s:: %s Precip %s' % (source, title, PDICT3[opt]),
                 subtitle='Data from %s' % (subtitle,), titlefontsize=14
                 )

    idx0 = iemre.daily_offset(sdate)
    idx1 = iemre.daily_offset(edate) + 1
    if not os.path.isfile(ncfn):
        raise Exception("No data for that year, sorry.")
    nc = netCDF4.Dataset(ncfn, 'r')
    if state is not None:
        x0, y0, x1, y1 = util.grid_bounds(nc.variables['lon'][:],
                                          nc.variables['lat'][:],
                                          state_bounds[state])
    lats = nc.variables['lat'][y0:y1]
    lons = nc.variables['lon'][x0:x1]
    if (idx1 - idx0) < 32:
        p01d = distance(np.sum(nc.variables[ncvar][idx0:idx1, y0:y1, x0:x1],
                               0),
                        'MM').value('IN')
    else:
        # Too much data can overwhelm this app, need to chunk it
        for i in range(idx0, idx1, 10):
            i2 = min([i+10, idx1])
            if idx0 == i:
                p01d = distance(np.sum(nc.variables[ncvar][i:i2, y0:y1, x0:x1],
                                       0),
                                'MM').value('IN')
            else:
                p01d += distance(
                    np.sum(nc.variables[ncvar][i:i2, y0:y1, x0:x1], 0),
                    'MM').value('IN')
    nc.close()
    if np.ma.is_masked(np.max(p01d)):
        return 'Data Unavailable'
    units = 'inches'
    if opt == 'dep':
        # Do departure work now
        nc = netCDF4.Dataset(clncfn)
        climo = distance(np.sum(nc.variables[ncvar][idx0:idx1, y0:y1, x0:x1],
                                0), 'MM').value('IN')
        p01d = p01d - climo
        cmap = plt.get_cmap('RdBu')
        [maxv] = np.percentile(np.abs(p01d), [99, ])
        clevs = np.around(np.linspace(0 - maxv, maxv, 11), decimals=2)
    elif opt == 'per':
        nc = netCDF4.Dataset(clncfn)
        climo = distance(np.sum(nc.variables[ncvar][idx0:idx1, y0:y1, x0:x1],
                                0), 'MM').value('IN')
        p01d = p01d / climo * 100.
        cmap = plt.get_cmap('RdBu')
        cmap.set_under('white')
        cmap.set_over('black')
        clevs = [1, 10, 25, 50, 75, 100, 125, 150, 200, 300, 500]
        units = 'percent'
    else:
        clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
        if days > 6:
            clevs = [0.01, 0.3, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20]
        if days > 29:
            clevs = [0.01, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30, 35]
        if days > 90:
            clevs = [0.01, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30, 35, 40]
        cmap = nwsprecip()
        cmap.set_over('k')

    x2d, y2d = np.meshgrid(lons, lats)
    if ptype == 'c':
        mp.contourf(x2d, y2d, p01d, clevs, cmap=cmap, units=units,
                    iline=False)
    else:
        res = mp.pcolormesh(x2d, y2d, p01d, clevs, cmap=cmap, units=units)
        res.set_rasterized(True)
    if sector != 'midwest':
        mp.drawcounties()
        mp.drawcities()
    if usdm == 'yes':
        mp.draw_usdm(edate, filled=False, hatched=True)

    return mp.fig


if __name__ == '__main__':
    plotter(dict())
