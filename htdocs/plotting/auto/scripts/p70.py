import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable
import calendar
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This chart shows the period between the first
    and last watch, warning, advisory (WWA) issued by an office per year. The
    right hand chart displays the number of unique WWA events issued for
    that year.
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
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'DMX')[:4]
    phenomena = fdict.get('phenomena', 'SV')
    significance = fdict.get('significance', 'W')

    nt = NetworkTable('WFO')

    cursor.execute("""
        SELECT extract(year from issue) as yr, min(issue), max(issue),
        count(distinct eventid)
        from warnings where wfo = %s and phenomena = %s and significance = %s
        GROUP by yr ORDER by yr ASC
    """, (station, phenomena, significance))

    rows = []
    for row in cursor:
        rows.append(dict(year=int(row[0]), startdoy=int(row[1].strftime("%j")),
                         enddoy=int(row[2].strftime("%j")), count=int(row[3])))
    df = pd.DataFrame(rows)

    ends = np.array(df['enddoy'])
    starts = np.array(df['startdoy'])
    years = np.array(df['year'])

    thisyear = datetime.datetime.now().year

    fig = plt.Figure()
    ax = plt.axes([0.1, 0.1, 0.7, 0.8])

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

    ax = plt.axes([0.82, 0.1, 0.13, 0.8])
    ax.barh(years-0.4, df['count'], fc='blue')
    ax.set_ylim(years[0]-0.5, years[-1]+0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Events")

    return fig, df
