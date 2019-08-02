"""YTD precip"""
import calendar
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.network import Table as NetworkTable
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents year to date accumulated
    precipitation for a station of your choice.  The year with the highest and
    lowest accumulation is shown along with the envelop of observations and
    long term average.  You can optionally plot up to three additional years
    of your choice.
    """
    thisyear = datetime.date.today().year
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='year', name='year1', default=thisyear,
             label='Additional Year to Plot:'),
        dict(type='year', name='year2', optional=True, default=(thisyear - 1),
             label='Additional Year to Plot: (optional)'),
        dict(type='year', name='year3', optional=True, default=(thisyear - 2),
             label='Additional Year to Plot: (optional)'),
        ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    network = ctx['network']
    year1 = ctx.get('year1')
    year2 = ctx.get('year2')
    year3 = ctx.get('year3')
    nt = NetworkTable(network)
    table = "alldata_%s" % (station[:2],)
    df = read_sql("""
    WITH years as (SELECT distinct year from """ + table + """
        WHERE station = %s and sday = '0101')
    SELECT day, sday, year, precip,
    sum(precip) OVER (PARTITION by year ORDER by day ASC) as accum from
    """ + table + """ WHERE station = %s and year in (select year from years)
    ORDER by day ASC
    """, pgconn, params=(station, station), index_col='day')
    if df.empty:
        raise NoDataFound("No data found!")

    (fig, ax) = plt.subplots(1, 1)
    # Average
    jday = df[['sday', 'accum']].groupby('sday').mean()
    ax.plot(range(1, len(jday.index)+1), jday['accum'], lw=2, zorder=5,
            color='k', label='Average - %.2f' % (jday['accum'].iloc[-1],))

    # Min and Max
    jmin = df[['sday', 'accum']].groupby('sday').min()
    jmax = df[['sday', 'accum']].groupby('sday').max()
    ax.fill_between(range(1, len(jday.index)+1), jmin['accum'],
                    jmax['accum'], zorder=2, color='tan')

    # find max year
    plotted = []
    for year, color in zip([df['accum'].idxmax().year,
                            df[df['sday'] == '1231']['accum'].idxmin().year,
                            year1, year2, year3],
                           ['b', 'brown', 'r', 'g', 'purple']):
        if year is None or year in plotted:
            continue
        plotted.append(year)
        df2 = df[df['year'] == year]
        ax.plot(range(1, len(df2.index)+1), df2['accum'],
                label='%s - %.2f' % (year, df2['accum'].iloc[-1]),
                color=color, lw=2)

    ax.set_title(("Year to Date Accumulated Precipitation\n"
                  "[%s] %s (%s-%s)"
                  ) % (station, nt.sts[station]['name'],
                       nt.sts[station]['archive_begin'].year,
                       datetime.date.today().year))
    ax.set_ylabel("Precipitation [inch]")
    ax.grid(True)
    ax.legend(loc=2)
    ax.set_xlim(1, 366)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])

    return fig, df


if __name__ == '__main__':
    plotter(dict())
