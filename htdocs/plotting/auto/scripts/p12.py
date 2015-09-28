import psycopg2.extras
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable

PDICT = {'last': 'Last Date At or Above', 'first': 'First Date At or Above'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
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
    IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    threshold = int(fdict.get('threshold', 90))
    which = fdict.get('which', 'last')

    table = "alldata_%s" % (station[:2],)

    cursor.execute("""
    SELECT year,
    min(case when high >= %s then extract(doy from day) else 366 end) as nday,
    max(case when high >= %s then extract(doy from day) else 0 end) as xday,
    sum(case when high >= %s then 1 else 0 end) as count from """+table+"""
    WHERE station = %s GROUP by year ORDER by year ASC
    """, (threshold, threshold, threshold, station))
    years = []
    data = []
    count = []
    zeros = []
    for row in cursor:
        if row['count'] == 0:
            zeros.append(str(row['year']))
            continue
        count.append(row['count'])
        data.append(row['xday' if which == 'last' else 'nday'])
        years.append(row['year'])

    count = np.array(count)
    data = np.array(data)

    (fig, ax) = plt.subplots(1, 1)
    ax.scatter(data, count)
    ax.grid(True)
    ax.set_ylabel("Days At or Above High Temperature")
    ax.set_title(("%s [%s] Days per Year at or above %s $^\circ$F\nversus "
                  "%s Date of that Temperature") % (
                nt.sts[station]['name'], station, threshold,
                "Latest" if which == 'last' else 'First'))

    ax.text(data[-1]+1, count[-1], "%s" % (years[-1],), ha='left')
    xticks = []
    xticklabels = []
    for i in np.arange(min(data)-5, max(data)+5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_ylim(bottom=0)
    ax.set_xlabel(("Date of Last Occurrence" if which == 'last'
                   else 'Date of First Occurence'))

    ax2 = ax.twinx()
    sortvals = np.sort(data)
    yvals = np.arange(len(sortvals)) / float(len(sortvals))
    ax2.plot(sortvals, yvals * 100., color='r')
    ax2.set_ylabel("Accumulated Frequency [%] (red line)")

    avgd = datetime.datetime(2000, 1, 1) + datetime.timedelta(
                                            days=int(np.average(data)))
    ax.text(0.01, 0.99, ("%s year(s) failed threshold %s\nAvg Date: %s\n"
                         "Avg Count: %.1f days"
                         ) % (len(zeros),
                              ("[" +
                               ",".join(zeros) + "]"
                               ) if len(zeros) < 4 else "",
                              avgd.strftime("%-d %b"),
                              np.average(count)),
            transform=ax.transAxes, va='top', bbox=dict(color='white'))

    ax.set_xlim(min(data)-10, max(data)+10)

    idx = int(np.argmin(data))
    ax.text(data[idx]+1, count[idx], "%s" % (years[idx],),
            ha='left')
    idx = int(np.argmax(data))
    ax.text(data[idx]-1, count[idx], "%s" % (years[idx],),
            ha='right', va='bottom')
    idx = int(np.argmax(count))
    ax.text(data[idx], count[idx]+1, "%s" % (years[idx],),
            ha='center', va='bottom')

    return fig
