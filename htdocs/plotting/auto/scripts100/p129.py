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
    table = "alldata_%s" % (station[:2], )
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    years = (datetime.date.today().year -
             nt.sts[station]['archive_begin'].year + 1.0)

    plimit = '' if varname != 'precip' else ' and precip >= 0.01 '
    df = read_sql("""
    SELECT month,
    sum(case when """+varname+""" >= %s then 1 else 0 end) as hits,
    count(*)
    from """+table+"""
    WHERE station = %s """+plimit+"""
    GROUP by month ORDER by month ASC
    """, pgconn, params=(level, station), index_col='month')
    df['rank'] = (df['count'] - df['hits']) / df['count'] * 100.
    df['avg_days'] = df['hits'] / years

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index.values, df['rank'], fc='tan', zorder=1,
           ec='orange', align='edge', width=0.4)

    ax.set_title(("Monthly Frequency of Daily %s of %s+\nfor [%s] %s (%s-%s)"
                  ) % (PDICT[varname], level, station,
                       nt.sts[station]['name'],
                       nt.sts[station]['archive_begin'].year,
                       datetime.date.today().year))
    ax.grid(True)
    ax.set_ylabel("Percentile [%]", color='tan')
    ax.set_ylim(0, 105)
    ax2 = ax.twinx()
    ax2.bar(df.index.values, df['avg_days'], width=-0.4, align='edge',
            fc='blue', ec='k', zorder=1)
    ax2.set_ylabel("Avg # of Days per Month per Year (%.2f Total)" % (
                                            df['avg_days'].sum(),),
                   color='b')

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0.5, 12.5)
    for idx, row in df.iterrows():
        ax.text(idx, row['rank'], "%.1f" % (row['rank'],),
                ha='left', color='k', zorder=5, fontsize=11)
        ax2.text(idx, row['avg_days'], "%.1f" % (row['avg_days'],),
                 ha='right', color='k', zorder=5, fontsize=11)

    return fig, df

if __name__ == '__main__':
    plotter(dict())
