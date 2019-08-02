"""Temp drops in the fall"""

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot presents the largest drop in low
    temperature during a fall season.  The drop compares the lowest
    low previous to the date with the low for that date.  For example,
    if your coldest low to date was 40, you would not expect to see a
    low temperature of 20 the next night without first setting colder
    daily low temperatures. See also
    <a class="alert-link" href="/plotting/auto/?q=103">this autoplot</a>
    for more details."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:', network='IACLIMATE'),
        dict(type='year', name='year', default=2015,
             label='Year to Highlight'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    year = ctx['year']
    table = "alldata_%s" % (station[:2],)

    df = read_sql("""
      with data as (
        select day,
        (case when month < 6 then year - 1 else year end) as myyear,
        month, low,
        min(low)
        OVER (ORDER by day ASC ROWS between 121 PRECEDING and 1 PRECEDING) as p
        from """ + table + """ where station = %s)

      SELECT myyear as year, max(p - low) as largest_change, count(*) from data
      GROUP by year ORDER by year ASC
    """, pgconn, params=(station,), index_col='year')
    if df.empty:
        raise NoDataFound("No Data Found.")
    # remove in-progress years
    df = df[df['count'] > 122]

    (fig, ax) = plt.subplots(1, 1, sharex=True, figsize=(8, 6))
    ax.bar(df.index.values, 0 - df['largest_change'], fc='b', ec='b', zorder=1)
    ax.bar(year, 0 - df.at[year, 'largest_change'], fc='red', ec='red',
           zorder=2)
    ax.axhline(0 - df['largest_change'].mean(), lw=2, color='k')
    ax.grid(True)
    ax.set_ylabel(("Largest Low Temp Drop $^\circ$F, Avg: %.1f"
                   ) % (df['largest_change'].mean(),))
    ax.set_xlabel("%s value is %s" % (year, df.at[year, 'largest_change']))
    ax.set_title(("%s %s\n"
                  "Max Jul-Dec Low Temp Drop Exceeding "
                  "Previous Min Low for Fall"
                  ) % (station, ctx['_nt'].sts[station]['name']))
    ax.set_xlim(df.index.values.min() - 1, df.index.values.max() + 1)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
