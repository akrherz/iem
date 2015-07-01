import psycopg2.extras
import numpy as np
from pyiem import network
import datetime
import pandas as pd
import calendar

PDICT = {'high': 'High Temperature',
         'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart presents two measures of temperature
    variability.  The first is the standard deviation of the period of
    record for a given day of the year.  The second is the standard deviation
    of the day to day changes in temperature.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', name='var', default='high',
             label='Which Daily Variable:', options=PDICT),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    varname = fdict.get('var', 'high')
    if PDICT.get(varname) is None:
        return

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
    with data as (
        select extract(doy from day) as doy,
        day, """+varname+""" as v from """+table+""" WHERE
        station = %s),
    doyagg as (
        SELECT doy, stddev(v) from data GROUP by doy),
    deltas as (
        SELECT doy, (v - lag(v) OVER (ORDER by day ASC)) as d from data),
    deltaagg as (
        SELECT doy, stddev(d) from deltas GROUP by doy)

    SELECT d.doy, d.stddev, y.stddev from deltaagg d JOIN doyagg y ON
    (y.doy = d.doy) WHERE d.doy < 366 ORDER by d.doy ASC
    """, (station, ))
    rows = []
    for row in ccursor:
        rows.append(dict(doy=row[0], d2d_stddev=row[1],
                         doy_stddev=row[2]))
    df = pd.DataFrame(rows)

    fig, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(df['doy'], df['doy_stddev'], lw=2, color='r',
               label='Single Day')
    ax[0].plot(df['doy'], df['d2d_stddev'], lw=2, color='b',
               label='Day to Day')
    ax[0].legend(loc='best', fontsize=10, ncol=2)

    ax[0].set_ylabel("Temperature Std. Deviation $^\circ$F")
    ax[0].grid(True)

    msg = ("[%s] %s Daily %s Standard Deviations"
           ) % (station, nt.sts[station]['name'], PDICT.get(varname))
    tokens = msg.split()
    sz = len(tokens) / 2
    ax[0].set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    ax[1].plot(df['doy'], df['doy_stddev'] / df['d2d_stddev'], lw=2,
               color='g')
    ax[1].set_ylabel("Ratio SingleDay/Day2Day")
    ax[1].grid(True)
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                      305, 335, 365))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 366)
    return fig, df
