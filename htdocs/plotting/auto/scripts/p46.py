"""Min wind chill frequency"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

MDICT = OrderedDict([
         ('all', 'No Month/Time Limit'),
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('jan', 'January'),
         ('feb', 'February'),
         ('mar', 'March'),
         ('apr', 'April'),
         ('may', 'May'),
         ('jun', 'June'),
         ('jul', 'July'),
         ('aug', 'August'),
         ('sep', 'September'),
         ('oct', 'October'),
         ('nov', 'November'),
         ('dec', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents the frequency of observed
    minimum wind chill for a winter season each year over the period of
    record for the observation site."""
    desc['cache'] = 86400
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
        dict(type='select', name='month', default='all',
             label='Limit plot by month/season', options=MDICT),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    offset = 0
    if ctx['month'] == 'all':
        months = range(1, 13)
        offset = 3
    elif ctx['month'] == 'fall':
        months = [9, 10, 11]
    elif ctx['month'] == 'winter':
        months = [12, 1, 2]
        offset = 3
    elif ctx['month'] == 'spring':
        months = [3, 4, 5]
    elif ctx['month'] == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+ctx['month']+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    nt = NetworkTable(network)

    df = read_sql("""
        SELECT extract(year from valid + '%s months'::interval) as year,
         min(wcht(tmpf::numeric,(sknt*1.15)::numeric)) as min_windchill
         from alldata WHERE station = %s and sknt >= 0 and tmpf < 32
         and extract(month from valid) in %s
         GROUP by year ORDER by year ASC
      """, pgconn, params=(offset, station, tuple(months)),
                  index_col='year')

    ys = []
    freq = []
    sz = float(len(df.index))
    for lev in range(
            int(df['min_windchill'].max()), int(df['min_windchill'].min()) - 1,
            -1):
        freq.append(len(df[df['min_windchill'] < lev].index) / sz * 100.0)
        ys.append(lev)
    ys = np.array(ys)

    (fig, ax) = plt.subplots(2, 1, figsize=(8, 6))

    ax[0].barh(ys - 0.4, freq, ec='b', fc='b')
    # ax[0].set_ylim(-60.5, 0.5)
    ax[0].set_ylabel(r"Minimum Wind Chill $^\circ$F")
    ax[0].set_xlabel("Frequency [%]")
    ax[0].set_title(("[%s] %s %.0f-%.0f\n"
                     "Frequency of Observed Wind Chill over %s"
                     ) % (station, nt.sts[station]['name'],
                          df.index[0], df.index[-1], MDICT[ctx['month']]))
    ax[0].set_xticks([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100])
    ax[0].grid(True)

    ax[1].bar(df.index.values, df['min_windchill'], fc='b', ec='b')
    ax[1].set_ylabel(r"Minimum Wind Chill $^\circ$F")
    ax[1].grid(True)
    if offset > 0:
        ax[1].set_xlabel("Year label for spring portion of season")

    return fig, df


if __name__ == '__main__':
    plotter(dict())
