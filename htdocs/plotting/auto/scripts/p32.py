"""Daily departures"""
import datetime

import psycopg2
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context

PDICT = {'high': 'High Temperature',
         'low': 'Low Temperature',
         'avg': 'Daily Average Temperature'}
OPTDICT = {'diff': 'Difference in Degrees F',
           'sigma': 'Difference in Standard Deviations'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot presents the daily high, low, or
    average temperature departure.  The average temperature is simply the
    average of the daily high and low.  The daily climatology is simply based
    on the period of record observations for the site."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Year to Plot:'),
        dict(type="select", name='var', default='high', options=PDICT,
             label='Select Variable to Plot'),
        dict(type="select", name='how', default='diff', options=OPTDICT,
             label='How to express the difference'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    year = ctx['year']
    varname = ctx['var']
    how = ctx['how']

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    df = read_sql("""
    WITH data as (
     select day, high, low, (high+low)/2. as temp, sday
     from """+table+""" where station = %s and year = %s
    ), climo as (
     SELECT sday, avg(high) as avg_high, avg(low) as avg_low,
     avg((high+low)/2.) as avg_temp, stddev(high) as stddev_high,
     stddev(low) as stddev_low, stddev((high+low)/2.) as stddev_temp
     from """ + table + """ WHERE station = %s GROUP by sday
    )
    SELECT day,
    d.high - c.avg_high as high_diff,
    (d.high - c.avg_high) / c.stddev_high as high_sigma,
    d.low - c.avg_low as low_diff,
    (d.low - c.avg_low) / c.stddev_low as low_sigma,
    d.temp - c.avg_temp as avg_diff,
    (d.temp - c.avg_temp) / c.stddev_temp as avg_sigma,
    d.high,
    c.avg_high,
    d.low,
    c.avg_low,
    d.temp,
    c.avg_temp from
    data d JOIN climo c on
    (c.sday = d.sday) ORDER by day ASC
    """, pgconn, params=(station, year, station),
                  index_col=None)

    (fig, ax) = plt.subplots(1, 1)
    diff = df[varname+'_' + how]
    bars = ax.bar(df['day'].values, diff,  fc='b', ec='b', align='center')
    for i, bar in enumerate(bars):
        if diff[i] > 0:
            bar.set_facecolor('r')
            bar.set_edgecolor('r')
    ax.grid(True)
    if how == 'diff':
        ax.set_ylabel("Temperature Departure $^\circ$F")
    else:
        ax.set_ylabel("Temperature Std Dev Departure ($\sigma$)")
    ax.set_title(("%s %s\nYear %s %s Departure"
                  ) % (station, nt.sts[station]['name'], year,
                       PDICT[varname]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.DayLocator(1))

    return fig, df


if __name__ == '__main__':
    plotter(dict())
