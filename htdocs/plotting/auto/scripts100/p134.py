import psycopg2
import datetime
import numpy as np
from collections import OrderedDict
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context

PDICT = OrderedDict([('coldest_temp', 'Coldest Average Temperature'),
                     ('coldest_hitemp', 'Coldest Average High Temperature'),
                     ('coldest_lotemp', 'Coldest Average Low Temperature'),
                     ('warmest_temp', 'Warmest Average Temperature'),
                     ('warmest_hitemp', 'Warmest Average High Temperature'),
                     ('warmest_lotemp', 'Warmest Average Low Temperature'),
                     ('wettest', 'Highest Precipitation')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot displays the period of consecutive days
    each year with the extreme criterion meet. In the case of a tie, the
    first period of the season is used for the analysis.
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             network='IACLIMATE', label='Select Station:'),
        dict(type='select', name='var', default='coldest_temp',
             label='Which Metric', options=PDICT),
        dict(type="int", name="days", default=7,
             label='Over How Many Days?'),
    ]
    return d


def get_data(fdict):
    """ Get the data"""
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    days = ctx['days']
    varname = ctx['var']
    table = "alldata_%s" % (station[:2], )
    offset = 6 if varname.startswith('coldest') else 0
    df = read_sql("""
    WITH data as (
    SELECT day, extract(year from day + '%s months'::interval) as season,
    avg((high+low)/2.) OVER (ORDER by day ASC ROWS %s preceding) as avg_temp,
    avg(high) OVER (ORDER by day ASC ROWS %s preceding) as avg_hitemp,
    avg(low) OVER (ORDER by day ASC ROWS %s preceding) as avg_lotemp,
    sum(precip) OVER (ORDER by day ASC ROWS %s preceding) as sum_precip
    from """+table+""" WHERE station = %s),
    agg1 as (
        SELECT season, day, avg_temp,
        rank() OVER (PARTITION by season ORDER by avg_temp ASC)
            as coldest_temp_rank,
        rank() OVER (PARTITION by season ORDER by avg_hitemp ASC)
            as coldest_hitemp_rank,
        rank() OVER (PARTITION by season ORDER by avg_lotemp ASC)
            as coldest_lotemp_rank,
        rank() OVER (PARTITION by season ORDER by avg_temp DESC)
            as warmest_temp_rank,
        rank() OVER (PARTITION by season ORDER by avg_hitemp DESC)
            as warmest_hitemp_rank,
        rank() OVER (PARTITION by season ORDER by avg_lotemp DESC)
            as warmest_lotemp_rank,
        rank() OVER (PARTITION by season ORDER by sum_precip DESC)
            as wettest_rank,
        count(*) OVER (PARTITION by season)
        from data)
    SELECT season, day, extract(doy from day - '%s days'::interval) as doy,
    avg_temp from agg1 where """+varname+"""_rank = 1 and count > 270
    """, pgconn, params=(offset, days - 1, days - 1, days - 1, days - 1,
                         station, days - 1),
                  index_col='season')
    if varname.startswith('coldest'):
        df.loc[df['doy'] < 183, 'doy'] += 365.
    return df


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = ctx['network']
    days = ctx['days']
    varname = ctx['var']
    nt = NetworkTable(network)
    df = get_data(fdict)
    if len(df.index) == 0:
        return 'Error, no results returned!'

    ax = plt.axes([0.1, 0.3, 0.8, 0.6])
    lax = plt.axes([0.1, 0.1, 0.8, 0.2])
    title = PDICT.get(varname)
    if days == 1:
        title = title.replace("Average ", "")
    ax.set_title(("%s [%s]\n%i Day Period with %s"
                  ) % (nt.sts[station]['name'], station, days, title))
    ax.barh(df.index.values, [days]*len(df.index), left=df['doy'].values,
            edgecolor='tan', facecolor='tan')
    ax.grid(True)
    lax.grid(True)
    xticks = []
    xticklabels = []
    for i in np.arange(df['doy'].min() - 5, df['doy'].max() + 5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%-d %b"))
    ax.set_xticks(xticks)
    lax.set_xticks(xticks)
    lax.set_xticklabels(xticklabels)

    counts = np.zeros(366*2)
    for _, row in df.iterrows():
        counts[row['doy']:row['doy']+days] += 1

    lax.bar(np.arange(366*2), counts, edgecolor='blue', facecolor='blue')
    lax.set_ylabel("Years")
    lax.text(0.02, 0.9, "Frequency of Day\nwithin period",
             transform=lax.transAxes, va='top')
    ax.set_ylim(df.index.values.min() - 3, df.index.values.max() + 3)

    ax.set_xlim(df['doy'].min() - 10, df['doy'].max() + 10)
    lax.set_xlim(df['doy'].min() - 10, df['doy'].max() + 10)
    ax.yaxis.set_major_locator(MaxNLocator(prune='lower'))
    return plt.gcf(), df

if __name__ == '__main__':
    plotter(dict())
