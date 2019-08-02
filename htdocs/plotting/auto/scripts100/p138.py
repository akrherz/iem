"""monthly wind speeds"""
import calendar

from pandas.io.sql import read_sql
from pyiem import meteorology
from pyiem.plot.use_agg import plt
from pyiem.util import drct2text, get_autoplot_context, get_dbconn
from pyiem.datatypes import direction, speed
from pyiem.exceptions import NoDataFound

UNITS = {'mph': 'miles per hour',
         'kt': 'knots',
         'mps': 'meters per second'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This graph presents monthly average wind speed
    values along with vector-averaged average wind direction."""
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', name='units', default='mph',
             options=UNITS, label='Units of Average Wind Speed'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['zstation']
    units = ctx['units']
    df = read_sql("""
        select date_trunc('hour', valid at time zone 'UTC') as ts,
        avg(sknt) as sknt, max(drct) as drct from alldata
        WHERE station = %s and sknt is not null and drct is not null
        GROUP by ts
    """, pgconn, params=(station, ), index_col=None)
    if df.empty:
        raise NoDataFound("No Data Found.")
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
                  " Vector Average Direction"
                  ) % (station, ctx['_nt'].sts[station]['name'],
                       df['ts'].min().year,
                       df['ts'].max().year))

    return fig, grp


if __name__ == '__main__':
    plotter(dict())
