"""Consec days"""
import datetime
import calendar

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {'above': 'Temperature At or Above (AOA) Threshold',
         'below': 'Temperature Below Threshold'}
PDICT2 = {'high': 'High Temperature',
          'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart plots the frequency of having a streak
    of days above or below a given high or low temperature threshold."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:', network='IACLIMATE'),
        dict(type='select', name='var', default='high', options=PDICT2,
             label='Select which daily variable'),
        dict(type='select', name='dir', default='above', options=PDICT,
             label='Select temperature direction'),
        dict(type='int', name='threshold', default='60',
             label='Temperature Threshold (F):'),
        dict(type='int', name='days', default='7',
             label='Number of Days:')
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    days = ctx['days']
    threshold = ctx['threshold']
    varname = ctx['var']
    mydir = ctx['dir']

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    agg = "min" if mydir == 'above' else 'max'
    op = ">=" if mydir == 'above' else '<'
    df = read_sql("""
        with data as (select day,
        """+agg+"""("""+varname+""")
            OVER (ORDER by day ASC ROWS BETWEEN %s PRECEDING
        and CURRENT ROW) as agg from """ + table + """
        where station = %s)

    select extract(week from day) as week,
    sum(case when agg """+op+""" %s then 1 else 0 end)
        / count(*)::float * 100. as freq
    from data GROUP by week ORDER by week asc
    """, pgconn, params=(days - 1, station, threshold), index_col=None)

    fig, ax = plt.subplots(1, 1, sharex=True)

    label = "AOA" if mydir == 'above' else 'below'
    ax.set_title(("[%s] %s\nFrequency of %s Consec Days"
                  r" with %s %s %s$^\circ$F "
                  ) % (station, nt.sts[station]['name'],
                       days, varname.capitalize(), label, threshold))
    ax.set_ylabel("Frequency of Days [%]")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.bar(df['week'][:-1], df['freq'][:-1])

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    return fig, df


if __name__ == '__main__':
    plotter(dict())
