import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import numpy as np
from pyiem import network
import matplotlib.patheffects as PathEffects
import datetime
from scipy import stats
import pandas as pd
import calendar


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """For each year, the average first and last date of
    a given temperature is computed.  The values are then averaged and plotted
    to represent the period between these occurences and also the number of
    days represented by the period.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
    ]
    return d


def plotter(fdict):
    """ Go """
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    today = datetime.datetime.now()
    thisyear = today.year

    ccursor.execute("""
    with data as (
        select year, month, extract(doy from day) as doy,
        generate_series(32, high) as t from """ + table + """
        where station = %s and year < %s),
    agger as (
        SELECT year, t, min(doy), max(doy) from data GROUP by year, t)

    SELECT t, avg(min), avg(max) from agger GROUP by t ORDER by t ASC
    """, (station, thisyear))
    rows = []
    for row in ccursor:
        rows.append(dict(tmpf=row[0], min_jday=row[1],
                         max_jday=row[2]))
    df = pd.DataFrame(rows)

    fig = plt.figure()
    ax = plt.axes([0.1, 0.1, 0.7, 0.8])
    ax2 = plt.axes([0.81, 0.1, 0.15, 0.8])
    height = df['min_jday'][:] + 365. - df['max_jday']
    ax2.plot(height, df['tmpf'])
    ax2.set_xticks([30, 90, 180, 365])
    plt.setp(ax2.get_yticklabels(), visible=False)
    ax2.set_ylim(32, max(df['tmpf'])+5)
    ax2.grid(True)
    ax2.text(0.96, 0.02, "Days", transform=ax2.transAxes,
             bbox=dict(color='white'), ha='right')
    ax.text(0.96, 0.02, "Period", transform=ax.transAxes,
            bbox=dict(color='white'), ha='right')
    ax.set_ylim(32, max(df['tmpf'])+5)

    ax.barh(df['tmpf']-0.5, height, left=df['max_jday'], ec='tan', fc='tan',
            height=1.1)
    days = np.array([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305,
                     335])
    days = np.concatenate([days, days+365])
    ax.set_xticks(days)
    months = calendar.month_abbr[1:] + calendar.month_abbr[1:]
    ax.set_xticklabels(months)

    ax.set_ylabel("High Temperature $^\circ$F")
    ax.set_xlim(min(df['max_jday'])-1, max(df['max_jday']+height)+1)
    ax.grid(True)

    msg = ("[%s] %s Period Between Average Last and "
           "First High Temperature of Year"
           ) % (station, nt.sts[station]['name'])
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    return fig, df
