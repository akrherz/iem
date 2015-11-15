import psycopg2
import calendar
import datetime
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart presents the range between the warmest
    high temperature and the coldest low temperature for a given month for
    each year.  The bottom panel displays the range between those two values.
    The black lines represent the simple averages of the data.
    """
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='month', name='month', default=today.month,
             label='Month to Plot:'),
        dict(type='year', name='year', default=today.year,
             label='Year to Highlight:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200')
    month = int(fdict.get('month', 10))
    year = int(fdict.get('year', 2014))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    df = read_sql("""
    SELECT year,  max(high) as max_high,  min(low) as min_low
    from """+table+""" where station = %s and month = %s and
    high is not null and low is not null GROUP by year
    ORDER by year ASC
    """, pgconn, params=(station, month), index_col='year')

    df['rng'] = df['max_high'] - df['min_low']

    (fig, ax) = plt.subplots(2, 1, sharex=True)
    bars = ax[0].bar(df.index.values, df['rng'], bottom=df['min_low'],
                     fc='b', ec='b')
    idx = list(df.index.values.astype('i')).index(year)
    bars[idx].set_facecolor('r')
    bars[idx].set_edgecolor('r')
    ax[0].axhline(df['max_high'].mean(), lw=2, color='k', zorder=2)
    ax[0].text(df.index.values[-1]+2, df['max_high'].mean(),
               "%.0f" % (df['max_high'].mean(),),
               ha='left', va='center')
    ax[0].axhline(df['min_low'].mean(), lw=2, color='k', zorder=2)
    ax[0].text(df.index.values[-1]+2, df['min_low'].mean(),
               "%.0f" % (df['min_low'].mean(),),
               ha='left', va='center')
    ax[0].grid(True)
    ax[0].set_ylabel("Temperature $^\circ$F")
    ax[0].set_xlim(df.index.min()-1.5, df.index.max()+1.5)
    ax[0].set_title(("%s %s\n%s Temperature Range (Max High - Min Low)"
                     ) % (station, nt.sts[station]['name'],
                          calendar.month_name[month]))

    bars = ax[1].bar(df.index.values, df['rng'], fc='b', ec='b', zorder=1)
    bars[idx].set_facecolor('r')
    bars[idx].set_edgecolor('r')
    ax[1].set_title(("Year %s [Hi: %s Lo: %s Rng: %s] Highlighted"
                     ) % (year, df.at[year, 'max_high'],
                          df.at[year, 'min_low'], df.at[year, 'rng']),
                    color='r')
    ax[1].axhline(df['rng'].mean(), lw=2, color='k', zorder=2)
    ax[1].text(df.index.max()+2, df['rng'].mean(),
               "%.0f" % (df['rng'].mean(),),
               ha='left', va='center')
    ax[1].set_ylabel("Temperature Range $^\circ$F")
    ax[1].grid(True)

    return fig, df
