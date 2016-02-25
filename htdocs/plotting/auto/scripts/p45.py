import psycopg2
import datetime
import calendar
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """ Computes the frequency of having a day within
    a month with an overcast sky reported at a given time of the day.  There
    are a number of caveats to this plot as sensors and observing techniques
    have changed over the years!  The algorithm specifically looks for the
    OVC condition to be reported in the METAR observation.
    """
    d['data'] = True
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='hour', name='hour', label='Select Hour of Day:',
             default=12),
        dict(type='year', name='year',
             label='Select Year to Compare by Month:',
             default=today.year),
        dict(type='month', name='month',
             label='Select Month to Compare by Year:',
             default=today.year),
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
    hour = int(fdict.get('hour', 12))
    year = int(fdict.get('year', 2014))
    month = int(fdict.get('month', 2))

    nt = NetworkTable(network)

    df = read_sql("""
        WITH t as (
            SELECT tzname from stations WHERE id = %s and network = %s),
        obs as (
            SELECT to_char(valid, 'YYYYmmdd') as yyyymmdd,
            SUM(case when (skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC'
                        or skyc4 = 'OVC') then 1 else 0 end)
            from alldata JOIN t on (1=1) where station = %s
            and valid > '1951-01-01'
            and extract(hour from (valid at time zone t.tzname) +
                        '10 minutes'::interval ) = %s
            GROUP by yyyymmdd)

        SELECT substr(o.yyyymmdd,1,4)::int as year,
        substr(o.yyyymmdd,5,2)::int as month,
        sum(case when o.sum >= 1 then 1 else 0 end) as hits, count(*)
        from obs o GROUP by year, month ORDER by year ASC, month ASC
      """, pgconn, params=(station, network, station, hour),
                  index_col=None)
    df['freq'] = df['hits'] / df['count'] * 100.
    climo = df.groupby('month').sum()
    climo['freq'] = climo['hits'] / climo['count'] * 100.

    (fig, ax) = plt.subplots(2, 1)
    ax[0].bar(climo.index.values - 0.4,
              climo['freq'].values, fc='red', ec='red',
              width=0.4, label='Climatology')
    for i, row in climo.iterrows():
        ax[0].text(i - 0.25, row['freq']+1, "%.0f" % (row['freq'],),
                   ha='center')

    thisyear = df[df['year'] == year]
    if len(thisyear.index) > 0:
        ax[0].bar(thisyear['month'].values,
                  thisyear['freq'].values, fc='blue', ec='blue', width=0.4,
                  label=str(year))
    for i, row in thisyear.iterrows():
        ax[0].text(row['month'] + 0.25, row['freq'] + 1,
                   "%.0f" % (row['freq'],), ha='center')
    ax[0].set_ylim(0, 100)
    ax[0].set_xlim(0.5, 12.5)
    ax[0].legend(ncol=2)
    ax[0].set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax[0].set_xticks(range(1, 13))
    ax[0].grid(True)
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].set_ylabel("Frequency [%]")
    ax[0].set_title(("%s-%s [%s] %s\n"
                     "Frequency of %s Cloud Observation of Overcast"
                     ) % (nt.sts[station]['archive_begin'].year,
                          datetime.datetime.now().year, station,
                          nt.sts[station]['name'],
                          datetime.datetime(2000, 1, 1, hour,
                                            0).strftime("%I %p")))

    # Plot second one now
    obs = df[df['month'] == month]
    ax[1].bar(obs['year'].values, obs['freq'].values, fc='tan', ec='orange')
    ax[1].set_ylim(0, 100)
    ax[1].grid(True)
    ax[1].set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax[1].axhline(obs['freq'].mean())
    ax[1].set_ylabel("%s Frequency [%%]" % (calendar.month_abbr[month],))
    ax[1].set_xlim(obs['year'].min() - 2, obs['year'].max() + 2)
    return fig, df

if __name__ == '__main__':
    plotter(dict())
