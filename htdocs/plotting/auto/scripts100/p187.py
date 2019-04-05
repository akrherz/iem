"""Percentile Rank for station's data."""

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents the rank a station's yearly
    summary value has against an unweighted population of available
    observations in the state.  The green line is a simple average of the
    plot."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station:', network='IACLIMATE'),
        ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    nt = NetworkTable(ctx['network'])
    table = "alldata_%s" % (station[:2], )

    df = read_sql("""
    with data as (
        select station, year, sum(precip) from """ + table + """
        WHERE year >= 1893
        GROUP by station, year),
    stdata as (
        select year, sum from data where station = %s
    ),
    agg as (
        select station, year,
        avg(sum) OVER (PARTITION by year) as avgval,
        rank() OVER (PARTITION by year ORDER by sum ASC) /
        count(*) OVER (PARTITION by year)::float * 100. as percentile
        from data)
    select a.station, a.year, a.percentile, s.sum, a.avgval
    from agg a JOIN stdata s on (a.year = s.year)
    where a.station = %s ORDER by a.year ASC
    """, get_dbconn('coop'), params=(station, station), index_col='year')

    fig = plt.figure(figsize=(6, 7.5))
    ax = fig.add_axes([0.13, 0.52, 0.8, 0.4])
    meanval = df['percentile'].mean()
    bars = ax.bar(df.index.values, df['percentile'], color='b')
    for mybar in bars:
        if mybar.get_height() > meanval:
            mybar.set_color('red')
    ax.axhline(meanval, color='green', lw=2, zorder=5)
    ax.text(df.index.max() + 1, meanval, "%.1f" % (meanval, ), color='green')
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylabel("Percentile (no spatial weighting)")
    ax.grid(True)
    ax.set_title((
        "[%s] %s\nYearly Precip Total Percentile for all %s stations "
         ) % (station, nt.sts[station]['name'], station[:2])
    )

    # second plot
    ax = fig.add_axes([0.13, 0.07, 0.8, 0.4])
    ax.bar(df.index.values, df['sum'] - df['avgval'])
    meanval = (df['sum'] - df['avgval']).mean()
    ax.axhline(meanval, color='green', lw=2, zorder=5)
    ax.text(df.index.max() + 1, meanval, "%.2f" % (meanval, ), color='green')
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylabel("Bias to State Arithmetic Mean")
    ax.grid(True)

    return fig, df


if __name__ == '__main__':
    plotter(dict(station='IA0000', network='IACLIMATE'))
