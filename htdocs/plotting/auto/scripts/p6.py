import psycopg2
from pandas.io.sql import read_sql
from matplotlib import mlab
import calendar
import datetime
import numpy as np

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
    state.  The plot presents the distribution and normalized frequency
    for a specific year and for all years combined for the given month."""
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
    ptype_climo = "climo_%s" % (ptype.split("-")[1], )
    table = "alldata_%s" % (state,)

    df = read_sql("""
    WITH yearly as (
        SELECT station, year, sum(precip) as sum_precip,
        avg(high) as avg_high, avg(low) as avg_low,
        avg((high+low)/2.) as avg_temp from """ + table + """
        WHERE month = %s GROUP by station, year),
    agg1 as (
        SELECT station, avg(sum_precip) as precip,
        avg(avg_high) as high, avg(avg_low) as low,
        avg(avg_temp) as temp from yearly GROUP by station),
    thisyear as (
        SELECT station, sum_precip, avg_high, avg_low, avg_temp from yearly
        WHERE year = %s)

    SELECT a.station, a.precip as climo_precip, a.high as climo_high,
    a.low as climo_low, a.temp as climo_t,
    t.sum_precip as "sum-precip", t.avg_high as "avg-high",
    t.avg_low as "avg-low", t.avg_temp as "avg-t"
    FROM agg1 a JOIN thisyear t on (a.station = t.station)
    """, pgconn, params=(month, year), index_col='station')
    stateavg = df.at["%s0000" % (state, ), ptype]

    (fig, ax) = plt.subplots(1, 1)
    _, bins, _ = ax.hist(df[ptype].dropna(), 20, fc='lightblue',
                         ec='lightblue', normed=1)
    y = mlab.normpdf(bins, df[ptype].mean(), df[ptype].std())
    ax.plot(bins, y, 'b--', lw=2,
            label=("%s Normal Dist. $\sigma$=%.2f $\mu$=%.2f"
                   ) % (year, df[ptype].std(), df[ptype].mean()))

    _, bins = np.histogram(df[ptype_climo].dropna(), 20, normed=1)
    y = mlab.normpdf(bins, df[ptype_climo].mean(), df[ptype_climo].std())
    ax.plot(bins, y, 'g--', lw=2,
            label=("Climo Normal Dist. $\sigma$=%.2f $\mu$=%.2f"
                   ) % (df[ptype_climo].std(), df[ptype_climo].mean()))

    if stateavg is not None:
        ax.axvline(stateavg, label='%s Statewide Avg %.2f' % (year, stateavg),
                   color='b', lw=2)
    stateavg = df.at["%s0000" % (state, ), ptype_climo]
    if stateavg is not None:
        ax.axvline(stateavg, label='Climo Statewide Avg %.2f' % (stateavg,),
                   color='g', lw=2)
    ax.set_xlabel(PDICT[ptype])
    ax.set_ylabel("Normalized Frequency")
    ax.set_title(("%s %s %s %s Distribution\nNumber of stations: %s"
                  ) % (STATES[state], year, calendar.month_name[month],
                       PDICT[ptype], len(df.index)))
    ax.grid(True)
    box = ax.get_position()
    ax.set_position([box.x0, 0.25, box.width, 0.65])
    ax.legend(ncol=2, fontsize=12, loc=(-0.05, -0.3))

    return fig, df

if __name__ == '__main__':
    plotter({'type': 'avg-low', 'year': 2014, 'month': 12})
