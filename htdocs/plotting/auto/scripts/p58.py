import psycopg2.extras
import pandas as pd
import calendar
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """Displays the number of times that a single day's
    precipitation was greater than some portion of the monthly total. The
    default settings provide the frequency of getting half of the month's
    precipitation within one 24 hour period."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='text', name='threshold', default=50,
             label='Percentage of Monthly Precipitation on One Day'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA2203')
    threshold = float(fdict.get('threshold', 50.))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
         WITH monthly as (
         SELECT year, month, max(precip), sum(precip) from """+table+"""
         WHERE station = %s and precip is not null GROUP by year, month)

         SELECT month, sum(case when max > (sum * %s) then 1 else 0 end),
         count(*) from monthly GROUP by month ORDER by month ASC
         """, (station, threshold / 100.))
    df = pd.DataFrame(dict(freq=None, events=None,
                           month=pd.Series(calendar.month_abbr[1:],
                                           index=range(1, 13))),
                      index=pd.Series(range(1, 13), name='mo'))
    for row in cursor:
        df.at[row[0], 'events'] = row[1]
        df.at[row[0], 'freq'] = row[1] / float(row[2]) * 100.

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index - 0.4, df.freq)
    for i, row in df.iterrows():
        ax.text(i, row['freq']+2, "%.1f%%" % (row['freq'],), ha='center')
    ax.set_title(("[%s] %s\nFreq of One Day Having %.0f%% of That Month's "
                  "Precip Total"
                  ) % (station, nt.sts[station]['name'], threshold))
    ax.grid(True)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage of Years")
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xticks(range(1, 13))

    return fig, df
