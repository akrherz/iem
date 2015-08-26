"""
  Fall Minimum by Date
"""
import psycopg2.extras
import numpy as np
import calendar
import pandas as pd
from scipy import stats
from pyiem.network import Table as NetworkTable

PDICT = {'high': 'Daily High Temperature',
         'low': 'Daily Low Temperature',
         'avg': 'Daily Average Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot compares the distribution of daily
    temperatures for two months.  The quantiles for each month are computed
    and then plotted against each other.  This plot is typically called
    a quantile - quantile plot."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='month', name='month1', default='12',
             label='Select Month for x-axis:'),
        dict(type='month', name='month2', default='07',
             label='Select Month for y-axis:'),
        dict(type='select', name='var', default='high',
             label='Variable to Compare', options=PDICT),
        dict(type='text', label='x-axis Value to Highlight', default=55,
             name='highlight'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    month1 = int(fdict.get('month1', 12))
    month2 = int(fdict.get('month2', 7))
    highlight = int(fdict.get('highlight', 55))
    varname = fdict.get('var', 'high')
    if varname not in PDICT:
        return

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    # beat month
    cursor.execute("""
    SELECT month, high, low, (high+low)/2. from """+table+"""
    WHERE station = %s and month in (%s,%s)
    """, (station, month1, month2))

    data = {month1: [], month2: []}
    for row in cursor:
        data[row['month']].append(row[varname])

    p1 = np.percentile(data[month1], range(0, 101, 5))
    p2 = np.percentile(data[month2], range(0, 101, 5))
    df = pd.DataFrame({'%s_%s' % (calendar.month_abbr[month1],
                                  varname): pd.Series(p1),
                       '%s_%s' % (calendar.month_abbr[month2],
                                  varname): pd.Series(p2),
                       'quantile': pd.Series(range(0, 101, 5))})
    s_slp, s_int, s_r, _, _ = stats.linregress(p1, p2)

    (fig, ax) = plt.subplots(1, 1)

    ax.scatter(p1, p2, s=40, marker='s', color='b', zorder=3)
    ax.plot(p1, p1 * s_slp + s_int, lw=3, color='r',
            zorder=2, label=r"Fit R$^2$=%.2f" % (s_r ** 2,))
    ax.axvline(highlight, zorder=1, color='k')
    y = highlight * s_slp + s_int
    ax.axhline(y, zorder=1, color='k')
    ax.text(p1[0], y, "%.0f $^\circ$F" % (y,), va='center',
            bbox=dict(color='white'))
    ax.text(highlight, p2[0], "%.0f $^\circ$F" % (highlight,), ha='center',
            rotation=90, bbox=dict(color='white'))
    ax.set_title(("[%s] %s\n%s vs %s %s Quantile-Quantile Plot"
                  ) % (station, nt.sts[station]['name'],
                       calendar.month_abbr[month2],
                       calendar.month_abbr[month1], PDICT[varname]))
    ax.set_xlabel("%s %s $^\circ$F" % (calendar.month_name[month1],
                                       PDICT[varname]))
    ax.set_ylabel("%s %s $^\circ$F" % (calendar.month_name[month2],
                                       PDICT[varname]))
    ax.grid(True)
    ax.legend(loc=2)

    return fig, df
