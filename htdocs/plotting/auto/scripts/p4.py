"""IEMRE trailing"""
import datetime

import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.dates as mdates
from pyiem import iemre, reference
from pyiem.plot.use_agg import plt
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import get_autoplot_context, get_dbconn, ncopen


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """Using the gridded IEM ReAnalysis of daily
    precipitation.  This chart presents the areal coverage of some trailing
    number of days precipitation for a state of your choice.  This application
    does not properly account for the trailing period of precipitation during
    the first few days of January."""
    today = datetime.date.today()
    desc['arguments'] = [
        dict(type='year', name='year', default=today.year,
             label='Select Year', min=1893),
        dict(type='float', name='threshold', default='1.0',
             label='Precipitation Threshold [inch]'),
        dict(type='int', name='period', default='7',
             label='Over Period of Days'),
        dict(type='state', name='state', default='IA',
             label='For State'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    year = ctx['year']
    threshold = ctx['threshold']
    period = ctx['period']
    state = ctx['state']

    pgconn = get_dbconn('postgis')
    states = gpd.GeoDataFrame.from_postgis("""
    SELECT the_geom, state_abbr from states where state_abbr = %s
    """, pgconn, params=(state, ), index_col='state_abbr',
                                           geom_col='the_geom')

    nc = ncopen(iemre.get_daily_ncname(year))
    precip = nc.variables['p01d']
    czs = CachingZonalStats(iemre.AFFINE)
    hasdata = np.zeros((nc.dimensions['lat'].size,
                        nc.dimensions['lon'].size))
    czs.gen_stats(hasdata, states['the_geom'])
    for nav in czs.gridnav:
        grid = np.ones((nav.ysz, nav.xsz))
        grid[nav.mask] = 0.
        jslice = slice(nav.y0, nav.y0 + nav.ysz)
        islice = slice(nav.x0, nav.x0 + nav.xsz)
        hasdata[jslice, islice] = np.where(grid > 0, 1,
                                           hasdata[jslice, islice])
    hasdata = np.flipud(hasdata)
    datapts = np.sum(np.where(hasdata > 0, 1, 0))

    now = datetime.date(year, 1, 1)
    now += datetime.timedelta(days=(period-1))
    ets = datetime.date(year, 12, 31)
    today = datetime.date.today()
    if ets > today:
        ets = today
    days = []
    coverage = []
    while now <= ets:
        idx = iemre.daily_offset(now)
        sevenday = np.sum(precip[(idx-period):idx, :, :], 0)
        pday = np.where(hasdata > 0, sevenday[:, :], -1)
        tots = np.sum(np.where(pday >= (threshold * 25.4), 1, 0))
        days.append(now)
        coverage.append(tots / float(datapts) * 100.0)

        now += datetime.timedelta(days=1)
    df = pd.DataFrame(dict(day=pd.Series(days),
                           coverage=pd.Series(coverage)))

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(days, coverage, fc='g', ec='g')
    ax.set_title(("%s IEM Estimated Areal Coverage Percent of %s\n"
                  " receiving %.2f inches of rain over trailing %s day period"
                  ) % (year, reference.state_names[state], threshold, period))
    ax.set_ylabel("Areal Coverage [%]")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%-d'))
    ax.set_yticks(range(0, 101, 25))
    ax.grid(True)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
