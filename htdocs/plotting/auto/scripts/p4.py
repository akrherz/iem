"""IEMRE trailing"""
import datetime

import numpy as np
import netCDF4
import pandas as pd
from pyiem import iemre
from pyiem.util import get_autoplot_context
from pyiem import reference


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
        dict(type='clstate', name='state', default='IA',
             label='For State'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    ctx = get_autoplot_context(fdict, get_description())
    year = ctx['year']
    threshold = ctx['threshold']
    period = ctx['period']
    state = ctx['state']

    nc2 = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
    iowa = nc2.variables[state][:]
    iowapts = np.sum(np.where(iowa > 0, 1, 0))
    nc2.close()

    nc = netCDF4.Dataset('/mesonet/data/iemre/%s_mw_daily.nc' % (year, ))
    precip = nc.variables['p01d']

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
                  ) % (reference.state_names[state], threshold, period))
    ax.set_ylabel("Areal Coverage [%]")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.set_yticks(range(0, 101, 25))
    ax.grid(True)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
