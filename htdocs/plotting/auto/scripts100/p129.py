import psycopg2
import calendar
import datetime
import numpy as np
from pandas.io.sql import read_sql
from collections import OrderedDict
from pyiem.network import Table as NetworkTable

PDICT = OrderedDict([
    ('high', 'High Temperature'),
    ('low', 'Low Temperature'),
    ('precip', 'Precipitation')
    ])

PDICT2 = {'above': 'At or Above',
          'below': 'Below'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart plots the monthly percentiles that
    a given daily value has.  For example, where would a daily 2 inch
    precipitation rank for each month of the year.  Having a two inch event
    in December would certainly rank higher than one in May. Percentiles
    for precipitation are computed with dry days omitted."""
    d['arguments'] = [
        dict(type='select', options=PDICT, name='var',
             label='Select Variable to Plot', default='precip'),
        dict(type='select', options=PDICT2, name='dir',
             label='Direction of Percentile', default='above'),
        dict(type='text', name='level', default='2',
             label='Daily Variable Level (inch or degrees F):'),
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA2203').upper()
    varname = fdict.get('var', 'precip')[:10]
    level = float(fdict.get('level', 2))
    mydir = fdict.get('dir', 'above')
    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    years = (datetime.date.today().year -
             nt.sts[station]['archive_begin'].year + 1.0)

    plimit = '' if varname != 'precip' else ' and precip >= 0.01 '
    comp = ">=" if mydir == 'above' else "<"
    df = read_sql("""
    SELECT month,
    sum(case when """+varname+""" """+comp+""" %s then 1 else 0 end) as hits,
    count(*)
    from """+table+"""
    WHERE station = %s """+plimit+"""
    GROUP by month ORDER by month ASC
    """, pgconn, params=(level, station), index_col='month')
    df['rank'] = (df['count'] - df['hits']) / df['count'] * 100.
    df['avg_days'] = df['hits'] / years
    df['return_interval'] = 1.0 / df['avg_days']
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index.values, df['rank'], fc='tan', zorder=1,
           ec='orange', align='edge', width=0.4)

    units = 'inch' if varname in ['precip', ] else 'F'
    ax.set_title(("Monthly Frequency of Daily %s %s %s+ %s\n"
                  "for [%s] %s (%s-%s)"
                  ) % (PDICT[varname], PDICT2[mydir], level, units, station,
                       nt.sts[station]['name'],
                       nt.sts[station]['archive_begin'].year,
                       datetime.date.today().year))
    ax.grid(True)
    ax.set_ylabel("Percentile [%]", color='tan')
    ax.set_ylim(0, 105)
    ax2 = ax.twinx()
    ax2.bar(df.index.values, df['return_interval'], width=-0.4, align='edge',
            fc='blue', ec='k', zorder=1)
    ax2.set_ylabel("Return Interval (years) (%.2f Days per Year)" % (
                                            df['avg_days'].sum(),),
                   color='b')
    ax2.set_ylim(0, df['return_interval'].max() * 1.1)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0.5, 12.5)
    for idx, row in df.iterrows():
        ax.text(idx, row['rank'], "%.1f" % (row['rank'],),
                ha='left', color='k', zorder=5, fontsize=11)
        if not np.isnan(row['return_interval']):
            ax2.text(idx, row['return_interval'],
                     "%.1f" % (row['return_interval'],),
                     ha='right', color='k', zorder=5, fontsize=11)
        else:
            ax2.text(idx, 0., "n/a", ha='right')

    return fig, df

if __name__ == '__main__':
    plotter(dict())
