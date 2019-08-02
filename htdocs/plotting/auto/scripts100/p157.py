"""RH climatology"""
import calendar
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = {'above': 'Above Threshold',
         'below': 'Below Threshold'}
PDICT2 = {'max_rh': 'Daily Max RH',
          'min_rh': 'Daily Min RH'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """The IEM computes a daily maximum and minimum
    relative humidity value based on whatever observations were available
    for that calendar day.  This app presents these values along with
    a simple climatology computed by averaging the daily observations. You
    can also plot a frequency of the RH value being above or below
    some threshold. This frequency is grouped by week of the year to
    provide some smoothing to the metric."""
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc['arguments'] = [
        dict(type='zstation', name='station', default='DSM',
             label='Select Station', network='IA_ASOS'),
        dict(type='year', name='year',
             default=today.year,
             label='Start Year to Plot:'),
        dict(type='select', name='var', options=PDICT2,
             default='max_rh', label='Which Variable'),
        dict(type='select', name='dir', options=PDICT,
             default='above', label='Threshold Direction'),
        dict(type='int', name='thres',
             default=95,
             label='Threshold [%] for Frequency'),
    ]
    return desc


def nice(val):
    """Helper."""
    if val == 'M':
        return 'M'
    if val < 0.01 and val > 0:
        return 'Trace'
    return '%.2f' % (val, )


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('iem')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    year = ctx['year']
    threshold = ctx['thres']
    mydir = ctx['dir']
    varname = ctx['var']

    op = ">=" if mydir == 'above' else "<"
    df = read_sql("""
        SELECT day, extract(doy from day) as doy,
        extract(year from day) as year,
        extract(week from day) as week,
        max_rh, min_rh, avg_rh,
        case when """ + varname + """ """ + op + """ %s then 1 else 0 end
        as rh_exceed
        from summary s JOIN stations t
        ON (s.iemid = t.iemid) WHERE t.id = %s and t.network = %s
        and min_rh is not null and max_rh is not null
        ORDER by day ASC
    """, pgconn, params=(threshold, station, ctx['network']), index_col='day')
    if df.empty:
        raise NoDataFound("No Data Found.")

    thisyear = df[df['year'] == year]
    gdf = df.groupby('doy').mean()
    if gdf.empty or 'avg_rh' not in gdf.columns:
        raise NoDataFound("No Data Found.")
    wdf = df.groupby('week').mean()

    (fig, ax) = plt.subplots(1, 1)
    ax.plot(gdf.index.values, gdf['max_rh'].values, color='b', lw=2,
            label='Max')
    ax.plot(gdf.index.values, gdf['avg_rh'].values, color='g', lw=2,
            label='Avg')
    ax.plot(gdf.index.values, gdf['min_rh'].values, color='k', lw=2,
            label='Min')
    ax.plot(wdf.index.values * 7, wdf['rh_exceed'].values * 100.,
            color='r', lw=2)

    ax.bar(thisyear['doy'].values, thisyear['max_rh'] - thisyear['min_rh'],
           bottom=thisyear['min_rh'].values, ec='lightblue', fc='lightblue',
           label='%s Obs' % (year,))
    ax.legend(ncol=4, loc=(0.05, -0.2), fontsize=12)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_position([0.1, 0.2, 0.75, 0.7])
    ax.set_xlim(1, 365)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.set_title(("%s [%s] (%.0f-%.0f)\n"
                  "%.0f Daily Relative Humidity"
                  ) % (ctx['_nt'].sts[station]['name'], station,
                       df['year'].min(), df['year'].max(), year))
    ax2 = ax.twinx()
    ax2.set_ylabel("Daily Frequency w/ %s %s %.0f%%" % (varname, op,
                                                        threshold),
                   color='r')
    ax2.set_ylim(0, 100)
    ax2.set_position([0.1, 0.2, 0.75, 0.7])
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    return fig, df


if __name__ == '__main__':
    plotter(dict())
