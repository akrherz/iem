from pandas.io.sql import read_sql
import psycopg2
from pyiem import network
import sys
import numpy as np

PDICT = {'spring': '1 January - 30 June',
         'fall': '1 July - 31 December'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot analyzes the number of steps down in
    low temperature during the fall season and the number of steps up in
    high temperature during the spring season.  These steps are simply having
    a newer colder low or warmer high for the season to date period.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='select', name='season', options=PDICT,
             label='Select which half of year', default='fall'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody',
                                port=5555)

    station = fdict.get('station', 'IA2203')
    season = fdict.get('season', 'fall')
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    df = read_sql("""
    WITH obs as (
        SELECT day, year, month, high, low,
        case when month > 6 then 'fall' else 'spring' end as season
        from """ + table + """ WHERE station = %s),
    data as (
        SELECT year, season,
        max(high) OVER (PARTITION by year, season ORDER by day ASC
                        ROWS BETWEEN 183 PRECEDING and CURRENT ROW) as mh,
        min(low) OVER (PARTITION by year, season ORDER by day ASC
                       ROWS BETWEEN 183 PRECEDING and CURRENT ROW) as ml
        from obs),
    lows as (
        SELECT distinct year, ml as level, season from data
        where season = 'fall'),
    highs as (
        SELECT distinct year, mh as level, season from data
        where season = 'spring')

    SELECT year, level, season from lows UNION
    SELECT year, level, season from highs
    """, pgconn, params=[station])
    df2 = df[df['season'] == season]
    (fig, ax) = plt.subplots(2, 1)
    dyear = df2.groupby(['year']).count()
    ax[0].bar(dyear.index, dyear['level'], facecolor='tan', edgecolor='tan')
    ax[0].axhline(dyear['level'].mean(), lw=2)
    ax[0].set_ylabel("Yearly Events Avg: %.1f" % (dyear['level'].mean(), ))
    ax[0].set_xlim(dyear.index.min()-1, dyear.index.max()+1)
    title = "%s Steps %s" % (PDICT[season],
                             "Down" if season == 'fall' else 'Up')
    ax[0].set_title("%s [%s]\n%s in Temperature" % (nt.sts[station]['name'],
                                                    station, title))
    ax[0].grid(True)

    ax[1].hist(np.array(df2['level'], 'f'),
               bins=np.arange(df2['level'].min(),
                              df2['level'].max()+1, 2),
               normed=True, facecolor='tan')
    ax[1].set_ylabel("Probability Density")
    ax[1].axvline(32, lw=2)
    ax[1].grid(True)
    ax[1].set_xlabel("Temperature $^\circ$F, 32 degrees highlighted")

    return fig, df
