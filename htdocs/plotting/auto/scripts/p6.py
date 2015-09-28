import psycopg2.extras
import numpy as np
from matplotlib import mlab
import calendar
import datetime

PDICT = {'sum-precip': 'Total Precipitation [inch]',
         'avg-high': 'Average Daily High [F]',
         'avg-low': 'Average Daily Low [F]',
         'avg-t': 'Average Daily Temp [F]',
         }

STATES = {'IA': 'Iowa',
          'IL': 'Illinois',
          'MO': 'Missouri',
          'KS': 'Kansas',
          'NE': 'Nebraska',
          'SD': 'South Dakota',
          'ND': 'North Dakota',
          'MN': 'Minnesota',
          'WI': 'Wisconsin',
          'MI': 'Michigan',
          'OH': 'Ohio',
          'KY': 'Kentucky'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='clstate', name='state', default='IA',
             label='Select State:'),
        dict(type='year', name='year', default=today.year,
             label='Select Year'),
        dict(type='month', name='month', default='6', label='Select Month'),
        dict(type='select', name='type', default='sum-precip',
             label='Which metric to plot?', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    state = fdict.get('state', 'IA')
    year = int(fdict.get('year', 2014))
    month = int(fdict.get('month', 6))
    ptype = fdict.get('type', 'sum-precip')
    table = "alldata_%s" % (state,)

    data = []
    ccursor.execute("""
    SELECT station,
    sum(precip) as "sum-precip",
    avg(high) as "avg-high",
    avg(low) as "avg-low",
    avg((high+low)/2.) as "avg-t"
    from """+table+""" WHERE year = %s and month = %s GROUP by station
    """, (year, month))
    stateavg = None
    for row in ccursor:
        if row['station'][2:] == '0000':
            stateavg = row[ptype]
            continue
        if row['station'][2] == 'C':
            continue
        data.append(float(row[ptype]))

    data = np.array(data)

    (fig, ax) = plt.subplots(1, 1)
    n, bins, patches = ax.hist(data, 20, fc='lightblue', ec='lightblue', 
                               normed=1)
    y = mlab.normpdf(bins, np.average(data), np.std(data))
    ax.plot(bins, y, 'r--', lw=2,
            label=("Normal Dist.\n$\sigma$=%.2f $\mu$=%.2f"
                   ) % (np.std(data), np.average(data)))
    if stateavg is not None:
        ax.axvline(stateavg, label='Statewide Avg\n%.2f' % (stateavg,),
                   color='g', lw=2)
    ax.legend()
    ax.set_xlabel(PDICT[ptype])
    ax.set_ylabel("Normalized Frequency")
    ax.set_title(("%s %s %s %s Distribution\nNumber of stations: %s"
                  ) % (STATES[state], year, calendar.month_name[month],
                       PDICT[ptype], len(data)))
    ax.grid(True)

    return fig
