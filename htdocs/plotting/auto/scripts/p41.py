import psycopg2.extras
import numpy as np
import calendar
import pandas as pd
from scipy import stats
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context

PDICT = {'high': 'Daily High Temperature',
         'low': 'Daily Low Temperature',
         'avg': 'Daily Average Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot compares the distribution of daily
    temperatures for two months for a single station of your choice.  The
    left hand plot depicts a quantile - quantile plot, which simply plots
    the montly percentile values against each other.  You could think of this
    plot as comparable frequencies.  The right hand plot depicts the
    distribution of each month's temperatures expressed as a violin plot. These
    type of plots are useful to see the shape of the distribution.  These plots
    also contain the mean and extremes of the distributions."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             network='IACLIMATE', label='Select Station:'),
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
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = ctx['network']
    month1 = ctx['month1']
    month2 = ctx['month2']
    highlight = float(ctx['highlight'])
    varname = ctx['var']

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable(network)

    # beat month
    cursor.execute("""
    SELECT month, high, low, (high+low)/2. from """+table+"""
    WHERE station = %s and month in (%s,%s)
    """, (station, month1, month2))

    data = {month1: [], month2: []}
    for row in cursor:
        data[row['month']].append(row[varname])
    m1data = np.array(data[month1])
    m2data = np.array(data[month2])

    p1 = np.percentile(m1data, range(0, 101, 5))
    p2 = np.percentile(m2data, range(0, 101, 5))
    df = pd.DataFrame({'%s_%s' % (calendar.month_abbr[month1],
                                  varname): pd.Series(p1),
                       '%s_%s' % (calendar.month_abbr[month2],
                                  varname): pd.Series(p2),
                       'quantile': pd.Series(range(0, 101, 5))})
    s_slp, s_int, s_r, _, _ = stats.linregress(p1, p2)

    ax = plt.axes([0.1, 0.11, 0.5, 0.8])
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
    ax.set_title(("[%s] %s\n%s vs %s %s"
                  ) % (station, nt.sts[station]['name'],
                       calendar.month_abbr[month2],
                       calendar.month_abbr[month1], PDICT[varname]))
    ax.set_xlabel("%s %s $^\circ$F" % (calendar.month_name[month1],
                                       PDICT[varname]))
    ax.set_ylabel("%s %s $^\circ$F" % (calendar.month_name[month2],
                                       PDICT[varname]))
    ax.text(0.95, 0.05, "Quantile - Quantile Plot",
            transform=ax.transAxes, ha='right')
    ax.grid(True)
    ax.legend(loc=2)

    ax = plt.axes([0.7, 0.11, 0.27, 0.8])
    ax.set_title("Distribution")
    v1 = ax.violinplot(m1data, positions=[0, ], showextrema=True,
                       showmeans=True)
    b = v1['bodies'][0]
    m = np.mean(b.get_paths()[0].vertices[:, 0])
    b.get_paths()[0].vertices[:, 0] = np.clip(b.get_paths(
        )[0].vertices[:, 0], -np.inf, m)
    b.set_color('r')
    for l in ['cmins', 'cmeans', 'cmaxes']:
        v1[l].set_color('r')

    v1 = ax.violinplot(m2data, positions=[0, ], showextrema=True,
                       showmeans=True)
    b = v1['bodies'][0]
    m = np.mean(b.get_paths()[0].vertices[:, 0])
    b.get_paths()[0].vertices[:, 0] = np.clip(b.get_paths(
        )[0].vertices[:, 0], m, np.inf)
    b.set_color('b')
    for l in ['cmins', 'cmeans', 'cmaxes']:
        v1[l].set_color('b')

    p0 = plt.Rectangle((0, 0), 1, 1, fc="r")
    p1 = plt.Rectangle((0, 0), 1, 1, fc="b")
    ax.legend((p0, p1), (calendar.month_abbr[month1],
                         calendar.month_abbr[month2]),
              ncol=2, loc=(-0.18, -0.13))
    ax.set_ylabel("%s $^\circ$F" % (PDICT[varname],))
    ax.grid()

    return plt.gcf(), df

if __name__ == '__main__':
    plotter(dict())
