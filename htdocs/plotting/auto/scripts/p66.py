import psycopg2
import numpy as np
import datetime
import calendar
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql

PDICT = {'above': 'Temperature At or Above (AOA) Threshold',
         'below': 'Temperature Below Threshold'}
PDICT2 = {'high': 'High Temperature',
          'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart plots the frequency of having a streak
    of days above or below a given high or low temperature threshold."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='select', name='var', default='high', options=PDICT2,
             label='Select which daily variable'),
        dict(type='select', name='dir', default='above', options=PDICT,
             label='Select temperature direction'),
        dict(type='text', name='threshold', default='60',
             label='Temperature Threshold (F):'),
        dict(type='text', name='days', default='7',
             label='Number of Days:')
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA2203')
    days = int(fdict.get('days', 7))
    threshold = int(fdict.get('threshold', 60))
    varname = fdict.get('var', 'high')[:4]
    mydir = fdict.get('dir', 'above')[:5]

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
                  " with %s %s %s$^\circ$F "
                  ) % (station, nt.sts[station]['name'],
                       days, varname.capitalize(), label, threshold))
    ax.set_ylabel("Frequency of Days [%]")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.bar(np.arange(0, 52), df['freq'][:-1])

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    return fig, df
