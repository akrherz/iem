import psycopg2.extras
import numpy as np
import datetime
import calendar
import pandas as pd
from pyiem.network import Table as NetworkTable
from collections import OrderedDict

PDICT = OrderedDict([('high_over', 'High Temperature At or Above'),
                     ('high_under', 'High Temperature Below'),
                     ('low_over', 'Low Temperature At or Above'),
                     ('low_under', 'Low Temperature Below')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot displays the maximum number of consec
    days above or below some threshold for high or low temperature."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='select', name='var', default='high_under',
             label="Which Streak to Compute:", options=PDICT),
        dict(type="text", name='threshold', default=32,
             label="Temperature Threshold:")
    ]
    return d


def greater_than_or_equal(one, two):
    return (one >= two)


def less_than(one, two):
    return (one < two)


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    threshold = int(fdict.get('threshold', 32))
    varname = fdict.get('var', 'high_under')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
        SELECT extract(doy from day) as d, high, low
        from """+table+""" where station = %s ORDER by day ASC
    """, (station,))

    maxperiod = [0]*367
    running = 0
    col = 'high' if varname.find('high') == 0 else 'low'
    myfunc = greater_than_or_equal if varname.find('over') > 0 else less_than
    for row in cursor:
        if myfunc(row[col], threshold):
            running += 1
        else:
            running = 0
        if running > maxperiod[int(row['d'])]:
            maxperiod[int(row['d'])] = running

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    df = pd.DataFrame(dict(jdate=pd.Series(np.arange(0, 367)),
                           maxperiod=pd.Series(maxperiod)))
    (fig, ax) = plt.subplots(1, 1, sharex=True)
    ax.bar(np.arange(0, 367), maxperiod,  fc='b', ec='b')
    ax.grid(True)
    ax.set_ylabel("Consecutive Days")
    ax.set_title(("%s %s\nMaximum Straight Days with %s %s$^\circ$F"
                  ) % (station, nt.sts[station]['name'], PDICT[varname],
                       threshold))
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    return fig, df
