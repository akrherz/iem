import psycopg2
import datetime
from collections import OrderedDict
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
from pyiem import meteorology
from pyiem.util import drct2text
import pandas as pd
from pyiem.datatypes import direction, speed
import calendar

UNITS = {'mph': 'miles per hour',
         'kt': 'knots',
         'mps': 'meters per second'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This graph presents monthly average wind speed
    values along with vector-averaged average wind direction."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='select', name='units', default='mph',
             options=UNITS, label='Units of Average Wind Speed'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    units = fdict.get('units', 'mph')

    nt = NetworkTable(network)

    df = read_sql("""
        select date_trunc('hour', valid) as ts, avg(sknt) as sknt,
        max(drct) as drct from alldata
        WHERE station = %s and sknt is not null and drct is not null
        GROUP by ts
        """, pgconn, params=(station, ), parse_dates=('ts',),
                  index_col=None)
    sknt = speed(df['sknt'].values, 'KT')
    drct = direction(df['drct'].values, 'DEG')
    df['u'], df['v'] = [x.value('MPS') for x in meteorology.uv(sknt, drct)]
    df['month'] = df['ts'].dt.month
    grp = df[['month', 'u', 'v', 'sknt']].groupby('month').mean()
    grp['u_%s' % (units,)] = speed(grp['u'].values, 'KT').value(units.upper())
    grp['v_%s' % (units,)] = speed(grp['u'].values, 'KT').value(units.upper())
    grp['sped_%s' % (units,)] = speed(grp['sknt'].values,
                                      'KT').value(units.upper())
    drct = meteorology.drct(speed(grp['u'].values, 'KT'),
                            speed(grp['v'].values, 'KT'))
    grp['drct'] = drct.value('DEG')
    maxval = grp['sped_%s' % (units,)].max()
    (fig, ax) = plt.subplots(1, 1)
    ax.barh(grp.index.values, grp['sped_%s' % (units,)].values,
            align='center')
    ax.set_xlabel("Average Wind Speed [%s]" % (UNITS[units],))
    ax.set_yticks(grp.index.values)
    ax.set_yticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_xlim(0, maxval * 1.2)
    for mon, row in grp.iterrows():
        ax.text(maxval * 1.1, mon, drct2text(row['drct']), ha='center',
                va='center', bbox=dict(color='white'))
        ax.text(row['sped_%s' % (units,)] * 0.98, mon,
                "%.1f" % (row['sped_%s' % (units,)],), ha='right',
                va='center', bbox=dict(color='white',
                                       boxstyle='square,pad=0.03',))
    ax.set_ylim(12.5, 0.5)
    ax.set_title(("[%s] %s [%s-%s]\nMonthly Average Wind Speed and"
                  "Vector Average Direction"
                  ) % (station, nt.sts[station]['name'],
                       df['ts'].min().year,
                       df['ts'].max().year))

    return fig, grp

if __name__ == '__main__':
    plotter(dict())
