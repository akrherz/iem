"""Consec days"""
import datetime
import calendar
from collections import OrderedDict

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = OrderedDict([('high_over', 'High Temperature At or Above'),
                     ('high_under', 'High Temperature Below'),
                     ('low_over', 'Low Temperature At or Above'),
                     ('low_under', 'Low Temperature Below')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot displays the maximum number of consec
    days above or below some threshold for high or low temperature."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='select', name='var', default='high_under',
             label="Which Streak to Compute:", options=PDICT),
        dict(type="int", name='threshold', default=32,
             label="Temperature Threshold:")
    ]
    return desc


def greater_than_or_equal(one, two):
    """Helper."""
    return one >= two


def less_than(one, two):
    """Helper."""
    return one < two


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    threshold = ctx['threshold']
    varname = ctx['var']

    table = "alldata_%s" % (station[:2],)

    cursor.execute("""
        SELECT extract(doy from day)::int as d, high, low, day
        from """+table+""" where station = %s ORDER by day ASC
    """, (station,))

    maxperiod = [0]*367
    enddate = ['']*367
    running = 0
    col = 'high' if varname.find('high') == 0 else 'low'
    myfunc = greater_than_or_equal if varname.find('over') > 0 else less_than
    for row in cursor:
        doy = row['d']
        if myfunc(row[col], threshold):
            running += 1
        else:
            running = 0
        if running > maxperiod[doy]:
            maxperiod[doy] = running
            enddate[doy] = row['day']

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    df = pd.DataFrame(dict(mmdd=pd.date_range('1/1/2000',
                                              '12/31/2000').strftime("%m%d"),
                           jdate=pd.Series(np.arange(1, 367)),
                           maxperiod=pd.Series(maxperiod[1:]),
                           enddate=pd.Series(enddate[1:])))
    (fig, ax) = plt.subplots(1, 1, sharex=True)
    ax.bar(np.arange(1, 367), maxperiod[1:], fc='b', ec='b')
    ax.grid(True)
    ax.set_ylabel("Consecutive Days")
    ax.set_title(("%s %s\nMaximum Straight Days with %s %s$^\circ$F"
                  ) % (station, ctx['_nt'].sts[station]['name'],
                       PDICT[varname], threshold))
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
