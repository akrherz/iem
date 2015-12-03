import psycopg2
from pyiem import network
import matplotlib.patheffects as PathEffects
from pandas.io.sql import read_sql
from collections import OrderedDict
import datetime

PDICT = {'high': 'High Temperature',
         'low': 'Low Temperature',
         'avg': 'Average Temperature'}
MDICT = OrderedDict([
         ('all', 'No Month/Season Limit'),
         ('spring', 'Spring (MAM)'),
         ('fall', 'Fall (SON)'),
         ('winter', 'Winter (DJF)'),
         ('summer', 'Summer (JJA)'),
         ('jan', 'January'),
         ('feb', 'February'),
         ('mar', 'March'),
         ('apr', 'April'),
         ('may', 'May'),
         ('jun', 'June'),
         ('jul', 'July'),
         ('aug', 'August'),
         ('sep', 'September'),
         ('oct', 'October'),
         ('nov', 'November'),
         ('dec', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """The frequency of days per year that the temperature
    was above average.  Data is shown for the current year as well, so you
    should consider the representativity of that value when compared with
    other years with a full year's worth of data."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station'),
        dict(type='select', options=PDICT, name='var', default='high',
             label='Which variable to plot?'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0000')
    varname = fdict.get('var', 'high')
    month = fdict.get('month', 'all')

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    yr = "year as yr"
    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
        yr = "extract(year from o.day - '60 days'::interval) as yr"
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    df = read_sql("""
      WITH avgs as (
        SELECT sday, avg(high) as avg_high,
        avg(low) as avg_low,
        avg((high+low)/2.) as avg_temp from """ + table + """ WHERE
        station = %s GROUP by sday)

      SELECT """+yr+""",
      sum(case when o.high > a.avg_high then 1 else 0 end) as high_above,
      sum(case when o.low > a.avg_low then 1 else 0 end) as low_above,
      sum(case when (o.high+o.low)/2. > a.avg_temp then 1 else 0 end)
          as avg_above,
      count(*) as days from """ + table + """ o, avgs a WHERE o.station = %s
      and o.sday = a.sday and month in %s
      GROUP by yr ORDER by yr ASC
    """, pgconn, params=(station, station, tuple(months)),
                  index_col='yr')

    df['high_freq'] = df['high_above'] / df['days'].astype('f') * 100.
    df['low_freq'] = df['low_above'] / df['days'].astype('f') * 100.
    df['avg_freq'] = df['avg_above'] / df['days'].astype('f') * 100.

    (fig, ax) = plt.subplots(1, 1)
    avgv = df[varname+'_freq'].mean()

    colorabove = 'r'
    colorbelow = 'b'
    data = df[varname+'_freq'].values
    bars = ax.bar(df.index.values - 0.4, data, fc=colorabove,
                  ec=colorabove)
    for i, bar in enumerate(bars):
        if data[i] < avgv:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2)
    txt = ax.text(bars[10].get_x(), avgv, "Avg: %.1f%%" % (avgv,),
                  color='yellow', fontsize=14, va='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=5,
                                                 foreground="k")])
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_xlabel("Year")
    ax.set_xlim(bars[0].get_x() - 1, bars[-1].get_x() + 1)
    ax.set_ylabel("Frequency [%]")
    ax.grid(True)
    msg = ("[%s] %s %s-%s Percentage of Days with %s Above Average (month=%s)"
           ) % (station, nt.sts[station]['name'],
                df.index.values.min(), df.index.values.max(),
                PDICT[varname], month.upper())
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    return fig, df
