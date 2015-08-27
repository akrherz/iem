import psycopg2.extras
import datetime
import calendar
import numpy as np
import pandas as pd
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
        dict(type='year', name='year', label='Select Year to Compare:',
             default=today.year),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    hour = int(fdict.get('hour', 12))
    year = int(fdict.get('year', 2014))

    nt = NetworkTable(network)

    cursor.execute("""
        WITH t as (
            SELECT tzname from stations WHERE id = %s and network = %s),
        obs as (
            SELECT to_char(valid, 'YYYYmmdd') as yyyymmdd,
            SUM(case when (skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC'
                        or skyc4 = 'OVC') then 1 else 0 end)
            from alldata JOIN t on (1=1) where station = %s
            and extract(hour from (valid at time zone t.tzname) +
                        '10 minutes'::interval ) = %s
            GROUP by yyyymmdd),

        monthly as (
            SELECT substr(o.yyyymmdd,1,4) as year,
            substr(o.yyyymmdd,5,2) as month,
            sum(case when o.sum >= 1 then 1 else 0 end), count(*)
            from obs o GROUP by year, month)

        SELECT month,
        max(case when year::numeric = %s then sum else 0 end) as one,
        max(case when year::numeric = %s then count else 0 end) as two,
        sum(sum) as three, sum(count) as four
        from monthly GROUP by month ORDER by month ASC
      """, (station, network, station, hour, year, year))

    monthly = []
    thisyear = []
    for row in cursor:
        if row['one'] is None or row['two'] is None or row['two'] == 0:
            thisyear.append(np.nan)
        else:
            thisyear.append(float(row['one']) / float(row['two']) * 100.)
        monthly.append(float(row['three']) / float(row['four']) * 100.)

    df = pd.DataFrame({'thisyear': pd.Series(thisyear),
                       'month': pd.Series(range(1, 13)),
                       'climo': pd.Series(monthly)})

    (fig, ax) = plt.subplots(1, 1)
    bars = ax.bar(np.arange(1, 13) - 0.4, monthly, fc='red', ec='red',
                  width=0.4, label='Climatology')
    for i, _ in enumerate(bars):
        ax.text(i+1-0.25, monthly[i]+1, "%.0f" % (monthly[i],), ha='center')
    bars = ax.bar(np.arange(1, 13), thisyear, fc='blue', ec='blue', width=0.4,
                  label=str(year))
    for i, _ in enumerate(bars):
        if not np.isnan(thisyear[i]):
            ax.text(i+1+0.25, thisyear[i]+1, "%.0f" % (thisyear[i],),
                    ha='center')
    ax.set_ylim(0, 100)
    ax.set_xlim(0.5, 12.5)
    ax.legend()
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_xticks(range(1, 13))
    ax.grid(True)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_ylabel("Frequency [%]")
    ax.set_title(("%s-%s [%s] %s\n"
                  "Frequency of %s Cloud Observation of Overcast"
                  ) % (nt.sts[station]['archive_begin'].year,
                       datetime.datetime.now().year, station,
                       nt.sts[station]['name'],
                       datetime.datetime(2000, 1, 1, hour,
                                         0).strftime("%I %p")))

    return fig, df
