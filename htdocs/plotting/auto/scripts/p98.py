import psycopg2.extras
import numpy as np
from pyiem import network
import pandas as pd
import calendar

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
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    varname = fdict.get('var', 'precip')
    month = int(fdict.get('month', 9))
    threshold = float(fdict.get('thres', 90))
    if PDICT.get(varname) is None:
        return
    drct = fdict.get('dir', 'above')
    if PDICT2.get(drct) is None:
        return
    operator = ">=" if drct == 'above' else 'below'
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
        SELECT sday,
        sum(case when """+varname+""" """+operator+""" %s then 1 else 0 end),
        count(*)
        from """+table+""" WHERE station = %s and month = %s
        GROUP by sday ORDER by sday ASC
        """, (threshold, station, month))
    rows = []
    for row in ccursor:
        rows.append(dict(sday=row[0], hit=row[1], total=row[2]))
    df = pd.DataFrame(rows)
    df['freq'] = df['hit'] / df['total'] * 100.

    fig, ax = plt.subplots(1, 1)
    bars = ax.bar(np.arange(1, len(rows)+1)-0.4, df['freq'])
    for i, bar in enumerate(bars):
        ax.text(i+1, bar.get_height() + 0.3, '%s' % (df['hit'][i],),
                ha='center')
    msg = ("[%s] %s %s %s %s during %s (Avg: %.2f days/year)"
           ) % (station, nt.sts[station]['name'], PDICT.get(varname),
                PDICT2.get(drct), threshold, calendar.month_abbr[month],
                df['hit'].sum() / float(df['total'].sum()) * len(rows))
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))
    ax.set_ylabel("Frequency (%)")
    ax.set_xlabel(("Day of %s, years (out of %s) meeting criteria labelled"
                   ) % (calendar.month_name[month], np.max(df['total'],)))
    ax.grid(True)
    ax.set_xlim(0.5, 31.5)

    return fig, df
