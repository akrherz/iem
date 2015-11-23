import psycopg2
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents the largest drop in low
    temperature during a fall season.  The drop compares the lowest
    low previous to the date with the low for that date.  For example,
    if your coldest low to date was 40, you would not expect to see a
    low temperature of 20 the next night without first setting colder
    daily low temperatures. See also
    <a class="alert-link" href="/plotting/auto/?q=103">this autoplot</a>
    for more details."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200',
             label='Select Station:'),
        dict(type='year', name='year', default=2015,
             label='Year to Highlight'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200')
    year = int(fdict.get('year', 2015))
    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    df = read_sql("""
      with data as (
        select day,
        (case when month < 6 then year - 1 else year end) as myyear,
        month, low,
        min(low)
        OVER (ORDER by day ASC ROWS between 121 PRECEDING and 1 PRECEDING) as p
        from """ + table + """ where station = %s)

      SELECT myyear as year, max(p - low) as largest_change from data
      GROUP by year ORDER by year ASC
    """, pgconn, params=(station,), index_col='year')

    (fig, ax) = plt.subplots(1, 1, sharex=True)
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
                  ) % (station, nt.sts[station]['name']))
    ax.set_xlim(df.index.values.min() - 1, df.index.values.max() + 1)

    return fig, df
