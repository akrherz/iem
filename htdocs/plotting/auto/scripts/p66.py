import psycopg2.extras
import numpy as np
import datetime
import calendar
from pyiem.network import Table as NetworkTable
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart plots the frequency of having a streak
    of days above a given high temperature threshold."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='text', name='threshold', default='60',
             label='High Temperature Threshold:'),
        dict(type='text', name='days', default='7',
             label='Number of Days:')
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
    days = int(fdict.get('days', 7))
    threshold = int(fdict.get('threshold', 60))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    cursor.execute("""
        with data as (select day,
        min(high) OVER (ORDER by day ASC ROWS BETWEEN %s PRECEDING
        and CURRENT ROW) from """ + table + """
        where station = %s)

    select extract(week from day) as week,
    sum(case when min >= %s then 1 else 0 end) / count(*)::float
    from data GROUP by week ORDER by week asc""", (days - 1, station,
                                                   threshold))
    freq = np.zeros((53,), 'f')
    for row in cursor:
        freq[int(row[0]) - 1] = row[1] * 100.

    df = pd.DataFrame(dict(week=pd.Series(np.arange(1, 54)),
                           freq=pd.Series(freq)))
    fig, ax = plt.subplots(1, 1, sharex=True)

    ax.set_title(("[%s] %s\nFrequency of %s Consec Days"
                  " with High AOA %s$^\circ$F "
                  ) % (station, nt.sts[station]['name'],
                       days, threshold))
    ax.set_ylabel("Frequency of Days [%]")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.bar(np.arange(0, 52), freq[:-1])

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    return fig, df
