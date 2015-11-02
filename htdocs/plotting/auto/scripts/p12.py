import psycopg2
from pandas.io.sql import read_sql
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable

PDICT = {'last': 'Last Date At or Above', 'first': 'First Date At or Above'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot presents the yearly first or last date
    of a given high temperature along with the number of days that year above
    the threshold along with the cumulative distribution function for the
    first date!
    """
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='text', name='threshold', default='90',
             label='Enter Threshold:'),
        dict(type='select', name='which', default='last',
             label='Date Option:', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200')
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    threshold = int(fdict.get('threshold', 90))
    which = fdict.get('which', 'last')

    table = "alldata_%s" % (station[:2],)

    df = read_sql("""
    SELECT year,
    min(case when high >= %s then extract(doy from day) else 366 end) as nday,
    max(case when high >= %s then extract(doy from day) else 0 end) as xday,
    sum(case when high >= %s then 1 else 0 end) as count from """+table+"""
    WHERE station = %s and day >= '1893-01-01'
    GROUP by year ORDER by year ASC
    """, pgconn, params=(threshold, threshold, threshold, station),
                  index_col='year')
    # Set NaN where we did not meet conditions
    zeros = df[df['count'] == 0].index.values
    col = 'xday' if which == 'last' else 'nday'
    df2 = df[df['count'] > 0]

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(df2[col], df2['count'])
    ax.grid(True)
    ax.set_ylabel("Days At or Above High Temperature")
    ax.set_title(("%s [%s] Days per Year at or above %s $^\circ$F\nversus "
                  "%s Date of that Temperature") % (
                nt.sts[station]['name'], station, threshold,
                "Latest" if which == 'last' else 'First'))

    xticks = []
    xticklabels = []
    for i in np.arange(df2[col].min() - 5, df2[col].max() + 5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlabel(("Date of Last Occurrence" if which == 'last'
                   else 'Date of First Occurence'))

    ax2 = ax.twinx()
    sortvals = np.sort(df2[col].values)
    yvals = np.arange(len(sortvals)) / float(len(sortvals))
    ax2.plot(sortvals, yvals * 100., color='r')
    ax2.set_ylabel("Accumulated Frequency [%] (red line)")
    ax2.set_yticks([0, 25, 50, 75, 100])

    avgd = datetime.datetime(2000, 1, 1) + datetime.timedelta(
                                            days=int(df2[col].mean()))
    ax.text(0.01, 0.99, ("%s year(s) failed threshold %s\nAvg Date: %s\n"
                         "Avg Count: %.1f days"
                         ) % (len(zeros),
                              ("[" +
                               ",".join(zeros) + "]"
                               ) if len(zeros) < 4 else "",
                              avgd.strftime("%-d %b"),
                              df2['count'].mean()),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))

    ax.set_xlim(df2[col].min() - 10, df2[col].max() + 10)

    idx = df2[col].idxmax()
    ax.text(df2.at[idx, col] + 1, df2.at[idx, 'count'],
            "%s" % (idx,), ha='left')
    idx = df2[col].idxmin()
    ax.text(df2.at[idx, col] - 1, df2.at[idx, 'count'],
            "%s" % (idx,), va='bottom')
    idx = df2['count'].idxmax()
    ax.text(df2.at[idx, col] + 1, df2.at[idx, 'count'],
            "%s" % (idx,), va='bottom')

    return fig, df
