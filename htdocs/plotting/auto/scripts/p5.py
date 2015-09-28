import psycopg2.extras
import numpy as np
from pyiem import network
import calendar


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot displays the dates with the smallest
    difference between the high and low temperature by month. In the case
    of a tie, the first occurence is shown."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
    select month, to_char(day, 'Mon dd, YYYY'), high, low, rank() OVER
    (PARTITION by month ORDER by day DESC) from
    (select month, day, high, low, rank() OVER
        (PARTITION by month ORDER by (high-low) ASC) from """ + table + """
        where station = %s and high >= low) as foo
        WHERE rank = 1 ORDER by month ASC, day DESC
    """, (station, ))
    labels = []
    ranges = []
    for row in ccursor:
        if row[4] != 1:
            continue
        labels.append("%s (%s/%s) - %s" % (row[2]-row[3], row[2], row[3],
                                           row[1]))
        ranges.append(row[2] - row[3])

    (fig, ax) = plt.subplots(1, 1)

    ax.barh(np.arange(1, 13) - 0.4, ranges)
    for i in range(len(labels)):
        ax.text(ranges[i]+0.1, i+1, labels[i], va='center')
    ax.set_yticklabels(calendar.month_name)
    ax.set_yticks(range(0, 13))
    ax.set_ylim(0, 13)
    ax.set_xlim(0, max(ranges)+5)
    ax.set_xlabel("Date most recently set/tied shown")
    ax.set_title("%s [%s]\nMinimum Daily Temperature Range by Month" % (
                 nt.sts[station]['name'], station))

    return fig
