import psycopg2
from pyiem import network
import datetime
import pandas as pd
from pandas.io.sql import read_sql

PDICT = {'abs': 'Departure in degrees',
         'sigma': 'Depature in sigma'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot produces a timeseries difference between
    daily high and low temperatures against climatology.
    """
    d['data'] = True
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Which Year:'),
        dict(type='select', name='delta', options=PDICT,
             label='How to present the daily departures', default='abs'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0000')
    delta = fdict.get('delta', 'abs')
    year = int(fdict.get('year', datetime.date.today().year))
    nt = network.Table("%sCLIMATE" % (station[:2],))

    table = "alldata_%s" % (station[:2],)
    df = read_sql("""
        WITH days as (
            select generate_series('%s-01-01'::date, '%s-12-31'::date,
                '1 day'::interval)::date as day,
                to_char(generate_series('%s-01-01'::date, '%s-12-31'::date,
                '1 day'::interval)::date, 'mmdd') as sday
        ),
        climo as (
            SELECT sday, avg(high) as avg_high, stddev(high) as stddev_high,
            avg(low) as avg_low, stddev(low) as stddev_low from """+table+"""
            WHERE station = %s GROUP by sday
        ),
        thisyear as (
            SELECT day, sday, high, low from """+table+"""
            WHERE station = %s and year = %s
        ),
        thisyear2 as (
            SELECT d.day, d.sday, t.high, t.low from days d LEFT JOIN
            thisyear t on (d.sday = t.sday)
        )
        SELECT t.day, t.sday, t.high, t.low, c.avg_high, c.avg_low,
        c.stddev_high, c.stddev_low from thisyear2 t JOIN climo c on
        (t.sday = c.sday) ORDER by t.day ASC
    """, pgconn, params=(year, year, year, year,
                         station, station, year), index_col='day')
    df.index.name = 'Date'
    df['high_sigma'] = (df['high'] - df['avg_high']) / df['stddev_high']
    df['low_sigma'] = (df['low'] - df['avg_low']) / df['stddev_low']

    (fig, ax) = plt.subplots(2, 1, sharex=True)

    ax[0].plot(df.index, df.avg_high, color='r', linestyle='-',
               label='Climate High')
    ax[0].plot(df.index, df.avg_low, color='b', label='Climate Low')
    ax[0].set_ylabel(r"Temperature $^\circ\mathrm{F}$")
    ax[0].set_title("[%s] %s Climatology & %s Observations" % (
        station, nt.sts[station]['name'], year))

    ax[0].plot(df.index, df.high, color='brown',
               label='%s High' % (year,))
    ax[0].plot(df.index, df.low, color='green',
               label='%s Low' % (year,))

    if delta == 'abs':
        ax[1].plot(df.index, df.high - df.avg_high, color='r',
                   label='High Diff %s - Climate' % (year))
        ax[1].plot(df.index, df.low - df.avg_low, color='b',
                   label='Low Diff')
        ax[1].set_ylabel(r"Temp Difference $^\circ\mathrm{F}$")
    else:
        ax[1].plot(df.index, df.high_sigma, color='r',
                   label='High Diff %s - Climate' % (year))
        ax[1].plot(df.index, df.low_sigma, color='b',
                   label='Low Diff')
        ax[1].set_ylabel(r"Temp Difference $\sigma$")
        ymax = max([df.high_sigma.abs().max(), df.low_sigma.abs().max()]) + 1
        ax[1].set_ylim(0 - ymax, ymax)
    ax[1].legend(fontsize=10, ncol=2, loc='best')
    ax[1].grid(True)

    ax[0].legend(fontsize=10, ncol=2, loc=8)
    ax[0].grid()
    ax[0].xaxis.set_major_locator(
                               mdates.MonthLocator(interval=1)
                               )
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))

    return fig, df
