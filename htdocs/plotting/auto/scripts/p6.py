import psycopg2
from pandas.io.sql import read_sql
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
    d['description'] = """This application plots out the distribution of
    some monthly metric for single month for all tracked sites within one
    state."""
    d['data'] = True
    d['arguments'] = [
        dict(type='clstate', name='state', default='IA',
             label='Select State:'),
        dict(type='year', name='year', default=today.year,
             label='Select Year'),
        dict(type='month', name='month', default=today.month,
             label='Select Month'),
        dict(type='select', name='type', default='sum-precip',
             label='Which metric to plot?', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    state = fdict.get('state', 'IA')
    year = int(fdict.get('year', 2014))
    month = int(fdict.get('month', 6))
    ptype = fdict.get('type', 'sum-precip')
    table = "alldata_%s" % (state,)

    df = read_sql("""
    SELECT station,
    sum(precip) as "sum-precip",
    avg(high) as "avg-high",
    avg(low) as "avg-low",
    avg((high+low)/2.) as "avg-t"
    from """+table+""" WHERE year = %s and month = %s GROUP by station
    """, pgconn, params=(year, month), index_col='station')
    stateavg = df.at["%s0000" % (state, ), ptype]

    (fig, ax) = plt.subplots(1, 1)
    _, bins, _ = ax.hist(df[ptype], 20, fc='lightblue', ec='lightblue',
                         normed=1)
    y = mlab.normpdf(bins, df[ptype].mean(), df[ptype].std())
    ax.plot(bins, y, 'r--', lw=2,
            label=("Normal Dist.\n$\sigma$=%.2f $\mu$=%.2f"
                   ) % (df[ptype].std(), df[ptype].mean()))
    if stateavg is not None:
        ax.axvline(stateavg, label='Statewide Avg\n%.2f' % (stateavg,),
                   color='g', lw=2)
    ax.legend()
    ax.set_xlabel(PDICT[ptype])
    ax.set_ylabel("Normalized Frequency")
    ax.set_title(("%s %s %s %s Distribution\nNumber of stations: %s"
                  ) % (STATES[state], year, calendar.month_name[month],
                       PDICT[ptype], len(df.index)))
    ax.grid(True)

    return fig, df
