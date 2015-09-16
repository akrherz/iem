import psycopg2.extras
import numpy as np
import datetime
import calendar
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """
        Displays the warmest months on record for the site."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:')
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

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    records = [0]*12
    years = [0]*12
    oldrecords = [0]*12
    sigmas = [0]*12
    ssigmas = [0]*12
    avgs = [0]*12
    lastday = datetime.date.today()
    lastday = lastday.replace(day=1)
    cursor.execute("""
     SELECT month, stddev(avg), avg(avg) from (
      SELECT month, year, avg((high+low)/2.0) from """+table+""" where
      station = 'IA2203' and day < %s GROUP by year, month
     ) as foo GROUP by month """, (lastday, ))
    for row in cursor:
        sigmas[row[0]-1] = row[1]
        avgs[row[0]-1] = row[2]

    cursor.execute("""
     SELECT year, month, avg((high+low)/2.0) from """+table+""" where
     station = 'IA2203' and day < %s GROUP by year, month ORDER by avg ASC
    """, (lastday,))
    for row in cursor:
        idx = row[1]-1
        sigma = (row[2] - avgs[idx])/sigmas[idx]
        if row[2] > records[row[1]-1]:
            oldrecords[row[1]-1] = records[row[1]-1]
            records[row[1]-1] = float(row[2])
            years[row[1]-1] = row[0]
            ssigmas[idx] = sigma
    records = np.array(records)
    oldrecords = np.array(oldrecords)

    (fig, ax) = plt.subplots(2, 1)

    ax[0].bar(np.arange(1, 13) - 0.4, records, fc='pink')
    for i in range(12):
        ax[0].text(i+1, records[i]+2, "%s" % (years[i],), ha='center')
        ax[0].text(i+1, records[i]-10, "%.1f" % (records[i],), ha='center')
        ax[0].text(i+1, records[i]-20, "%.1f" % (ssigmas[i],), ha='center')
    ax[0].set_xlim(0.5, 12.5)
    ax[0].set_ylim(np.min(records)-30, 100)
    ax[0].set_title(("[%s] %s Warmest Months\n(high+low)/2 [%s-%s]\n"
                     "Year of maximum and its sigma departure shown"
                     ) % (station, nt.sts[station]['name'],
                          nt.sts[station]['archive_begin'].year, lastday.year))
    ax[0].set_ylabel("Avg Temp $^{\circ}\mathrm{F}$")
    ax[0].grid(True)
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].set_xticks(np.arange(1, 13))

    box = ax[0].get_position()
    ax[0].set_position([box.x0, box.y0, box.width, box.height * 0.8])

    ax[1].bar(np.arange(1, 13) - 0.4, records - oldrecords, fc='pink')
    ax[1].set_xlim(0.5, 12.5)
    ax[1].grid(True)
    ax[1].set_ylabel("Distance to 2nd $^{\circ}\mathrm{F}$")
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xticks(np.arange(1, 13))

    return fig
