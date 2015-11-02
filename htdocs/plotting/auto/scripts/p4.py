import numpy as np
import datetime
import netCDF4
from pyiem import iemre
import pandas as pd

STATES = {'IA': 'Iowa',
          'IL': 'Illinois',
          'MO': 'Missouri',
          'KS': 'Kansas',
          'NE': 'Nebraska',
          'SD': 'South Dakota',
          'ND': 'North Dakota',
          'MN': 'Minnesota',
          'WI': 'Wisconsin',
          'MI': 'Michigan',
          'OH': 'Ohio',
          'KY': 'Kentucky'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """Using the gridded IEM ReAnalysis of daily
    precipitation.  This chart presents the areal coverage of some trailing
    number of days precipitation for a state of your choice.  This application
    does not properly account for the trailing period of precipitation during
    the first few days of January."""
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='year', name='year', default=today.year,
             label='Select Year', min=1893),
        dict(type='text', name='threshold', default='1.0',
             label='Precipitation Threshold [inch]'),
        dict(type='text', name='period', default='7',
             label='Over Period of Days'),
        dict(type='clstate', name='state', default='IA', label='For State'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    year = int(fdict.get('year', 2014))
    threshold = float(fdict.get('threshold', 1))
    period = int(fdict.get('period', 7))
    state = fdict.get('state', 'IA')[:2]

    nc2 = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
    iowa = nc2.variables[state][:]
    iowapts = np.sum(np.where(iowa > 0, 1, 0))
    nc2.close()

    nc = netCDF4.Dataset('/mesonet/data/iemre/%s_mw_daily.nc' % (year, ))
    precip = nc.variables['p01d']

    now = datetime.datetime(year, 1, 1)
    now += datetime.timedelta(days=(period-1))
    ets = datetime.datetime(year, 12, 31)
    days = []
    coverage = []
    while now < ets:
        idx = iemre.daily_offset(now)
        sevenday = np.sum(precip[(idx-period):idx, :, :], 0)
        pday = np.where(iowa > 0, sevenday[:, :], -1)
        tots = np.sum(np.where(pday >= (threshold * 25.4), 1, 0))
        days.append(now)
        coverage.append(tots / float(iowapts) * 100.0)

        now += datetime.timedelta(days=1)
    df = pd.DataFrame(dict(day=pd.Series(days),
                           coverage=pd.Series(coverage)))

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(days, coverage, fc='g', ec='g')
    ax.set_title(("IEM Estimated Areal Coverage Percent of %s\n"
                  " receiving %.2f inches of rain over trailing %s day period"
                  ) % (STATES[state], threshold, period))
    ax.set_ylabel("Areal Coverage [%]")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.grid(True)
    return fig, df
