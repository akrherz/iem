import psycopg2
from pyiem.network import Table as NetworkTable
import datetime
import calendar
import numpy as np
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    ts = datetime.date.today()
    d['data'] = True
    d['description'] = """This chart displays the number of hourly
    observations each month that reported measurable precipitation.  Sites
    are able to report trace amounts, but those reports are not considered
    in hopes of making the long term climatology comparable.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='year', name='year', default=ts.year,
             label='Select Year:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    nt = NetworkTable(network)
    year = int(fdict.get('year', datetime.date.today().year))

    df = read_sql("""
    WITH obs as (
        SELECT distinct date_trunc('hour', valid) as t from alldata
        WHERE station = %s and p01i >= 0.01
    ), agg1 as (
        SELECT extract(year from t) as year, extract(month from t) as month,
        count(*) from obs GROUP by year, month
    ), averages as (
        SELECT month, avg(count), max(count) from agg1 GROUP by month
    ), myyear as (
        SELECT month, count from agg1 where year = %s
    ), ranks as (
        SELECT month, year,
        rank() OVER (PARTITION by month ORDER by count DESC)
        from agg1
    ), top as (
        SELECT month, max(year) as max_year from ranks
        WHERE rank = 1 GROUP by month
    ), agg2 as (
        SELECT t.month, t.max_year, a.avg, a.max from top t JOIN averages a
        on (t.month = a.month)
    )
    SELECT a.month, m.count, a.avg, a.max, a.max_year from
    agg2 a LEFT JOIN myyear m
    on (m.month = a.month) ORDER by a.month ASC
    """, pgconn, params=(station, year), index_col=None)
    if len(df.index) == 0:
        return "No Precipitation Data Found for Site"
    (fig, ax) = plt.subplots(1, 1)
    monthly = df['avg'].values.tolist()
    bars = ax.bar(df['month'] - 0.4, monthly, fc='red', ec='red',
                  width=0.4, label='Climatology')
    for i, _ in enumerate(bars):
        ax.text(i+1-0.25, monthly[i]+1, "%.0f" % (monthly[i],), ha='center')
    thisyear = df['count'].values.tolist()
    bars = ax.bar(np.arange(1, 13), thisyear, fc='blue', ec='blue', width=0.4,
                  label=str(year))
    for i, _ in enumerate(bars):
        if not np.isnan(thisyear[i]):
            ax.text(i+1+0.25, thisyear[i]+1, "%.0f" % (thisyear[i],),
                    ha='center')

    ax.scatter(df['month'], df['max'], marker='s', s=45, label="Max",
               zorder=2, color='g')
    for i, row in df.iterrows():
        ax.text(row['month'], row['max'], '%i\n%i.' % (row['max_year'],
                                                       row['max']), ha='right')
    ax.set_xticks(range(0, 13))
    ax.set_xticklabels(calendar.month_abbr)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, max([df['count'].max(), df['max'].max()]) * 1.2)
    ax.set_yticks(np.arange(0, df['max'].max() + 20,
                            12))
    ax.set_ylabel("Hours with 0.01+ inch precip")
    if datetime.date.today().year == year:
        ax.set_xlabel("Valid till %s" % (
            datetime.date.today().strftime("%-d %B"),))
    ax.grid(True)
    ax.legend(ncol=3)
    ax.set_title(("%s [%s]\n"
                  "Number of Hours with *Measurable* Precipitation Reported"
                  ) % (nt.sts[station]['name'], station))

    return fig, df

if __name__ == '__main__':
    plotter(dict(zstation='CGS', network='MD_ASOS', year=2016))
