import psycopg2
import numpy as np
from pyiem import network
from pandas.io.sql import read_sql
import calendar
from pyiem.util import get_autoplot_context

PDICT = {'precip': 'Daily Precipitation',
         'high': 'High Temperature',
         'low': 'Low Temperature'}

PDICT2 = {'above': 'At or Above Threshold',
          'below': 'Below Threshold'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot produces the daily frequency of
    a given criterion being meet for a station and month of your choice.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='month', name='month', default=9,
             label='Which Month:'),
        dict(type='select', name='var', default='high',
             label='Which Variable:', options=PDICT),
        dict(type='text', name='thres', default='90',
             label='Threshold (F or inch):'),
        dict(type='select', name='dir', default='above',
             label='Threshold Direction:', options=PDICT2),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    varname = ctx['var']
    month = ctx['month']
    threshold = float(ctx['thres'])
    if PDICT.get(varname) is None:
        return
    drct = ctx['dir']
    if PDICT2.get(drct) is None:
        return
    operator = ">=" if drct == 'above' else '<'
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    df = read_sql("""
        SELECT sday,
        sum(case when """+varname+""" """+operator+""" %s then 1 else 0 end)
        as hit,
        count(*) as total
        from """+table+""" WHERE station = %s and month = %s
        GROUP by sday ORDER by sday ASC
        """, COOP, params=(threshold, station, month), index_col='sday')
    df['freq'] = df['hit'] / df['total'] * 100.

    fig, ax = plt.subplots(1, 1)
    bars = ax.bar(np.arange(1, len(df.index)+1)-0.4, df['freq'])
    for i, bar in enumerate(bars):
        ax.text(i+1, bar.get_height() + 0.3, '%s' % (df['hit'][i],),
                ha='center')
    msg = ("[%s] %s %s %s %s during %s (Avg: %.2f days/year)"
           ) % (station, nt.sts[station]['name'], PDICT.get(varname),
                PDICT2.get(drct), threshold, calendar.month_abbr[month],
                df['hit'].sum() / float(df['total'].sum()) * len(df.index))
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.set_ylabel("Frequency (%)")
    ax.set_xlabel(("Day of %s, years (out of %s) meeting criteria labelled"
                   ) % (calendar.month_name[month], np.max(df['total'],)))
    ax.grid(True)
    ax.set_xlim(0.5, 31.5)
    ax.set_ylim(0, df['freq'].max() + 5)

    return fig, df

if __name__ == '__main__':
    plotter(dict(month=9, dir='below', thres=65, station='IA2724',
                 network='IACLIMATE'))
