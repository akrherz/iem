
import psycopg2.extras
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import datetime

STATES = {'IA': 'Iowa',
          'IL': 'Illinois',
          'KS': 'Kansas',
          'KY': 'Kentucky',
          'MI': 'Michigan',
          'MN': 'Minnesota',
          'MO': 'Missouri',
          'NE': 'Nebraska',
          'ND': 'North Dakota',
          'OH': 'Ohio',
          'SD': 'South Dakota',
          'WI': 'Wisconsin'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot displays the distribution of observed
    daily high and low temperatures for a given day and given state.  The
    dataset is fit with a simple normal distribution based on the simple
    population statistics.
    """
    d['arguments'] = [
        dict(type='clstate', name='state', default='IA',
             label='Which state?'),
        dict(type='month', name='month', default='10',
             label='Select Month:'),
        dict(type='day', name='day', default='7',
             label='Select Day:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    month = int(fdict.get('month', 10))
    day = int(fdict.get('day', 7))
    state = fdict.get('state', 'IA')
    table = "alldata_%s" % (state,)
    cursor.execute("""
    SELECT high, low from """+table+""" where sday = %s and
    high is not null and low is not null
     """, ("%02i%02i" % (month, day),))
    highs = []
    lows = []
    for row in cursor:
        highs.append(row[0])
        lows.append(row[1])
    highs = np.array(highs)
    lows = np.array(lows)

    (fig, ax) = plt.subplots(1, 1)

    ax.hist(highs, bins=(np.max(highs)-np.min(highs)),
            histtype='step', normed=True,
            color='r',  zorder=1)
    mu, std = norm.fit(highs)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ax.plot(x, p, 'r--', linewidth=2)

    ax.text(0.8, 0.99, ("High Temp\n$\mu$ = %.1f$^\circ$F\n$\sigma$ = %.2f"
                        "\n$n$ = %s") % (mu, std, len(highs)),
            va='top', ha='left', color='r',
            transform=ax.transAxes, bbox=dict(color='white'))

    ax.hist(lows, bins=(np.max(highs)-np.min(highs)),
            histtype='step', normed=True,
            color='b',  zorder=1)
    mu, std = norm.fit(lows)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ax.plot(x, p, 'b--', linewidth=2)

    ts = datetime.datetime(2000, month, day)
    ax.set_title("%s %s Temperature Distribution" % (STATES[state],
                                                     ts.strftime("%d %B")))

    ax.text(0.01, 0.99, ("Low Temp\n$\mu$ = %.1f$^\circ$F\n$\sigma$ = %.2f"
                         "\n$n$ = %s") % (mu, std, len(lows)),
            va='top', ha='left', color='b',
            transform=ax.transAxes, bbox=dict(color='white'))
    ax.grid(True)
    ax.set_xlabel("Temperature $^\circ$F")
    ax.set_ylabel("Probability")

    return fig
