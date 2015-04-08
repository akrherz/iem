import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable
import calendar


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """This chart shows the period between the first
    and last watch, warning, advisory issued by an office per year.
    """
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:'),
        dict(type='phenomena', name='phenomena',
             default='SV', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),

    ]
    return d


def plotter(fdict):
    """ Go """
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'DMX')[:4]
    phenomena = fdict.get('phenomena', 'SV')
    significance = fdict.get('significance', 'W')

    nt = NetworkTable('WFO')

    (fig, ax) = plt.subplots(1, 1, sharex=True)

    cursor.execute("""
        SELECT extract(year from issue) as yr, min(issue), max(issue)
        from warnings where wfo = %s and phenomena = %s and significance = %s
        GROUP by yr ORDER by yr ASC
    """, (station, phenomena, significance))

    years = []
    starts = []
    ends = []
    for row in cursor:
        years.append(int(row[0]))
        starts.append(int(row[1].strftime("%j")))
        ends.append(int(row[2].strftime("%j")))
    ends = np.array(ends)
    starts = np.array(starts)
    years = np.array(years)

    thisyear = datetime.datetime.now().year

    bars = ax.barh(years-0.4, (ends - starts), left=starts, fc='blue')
    if years[-1] == thisyear:
        bars[-1].set_facecolor('yellow')
    ax.set_title(("[%s] NWS %s\nPeriod between First and Last %s %s"
                  ) % (station, nt.sts[station]['name'],
                       vtec._phenDict[phenomena],
                       vtec._sigDict[significance]))
    ax.grid()
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
                   305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(1, 366)
    ax.set_ylabel("Year")
    ax.set_ylim(years[0]-0.5, years[-1]+0.5)

    return fig
