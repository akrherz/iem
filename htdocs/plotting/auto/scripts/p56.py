import psycopg2.extras
import pyiem.nws.vtec as vtec
import numpy as np
import datetime
import pandas as pd
from pyiem.network import Table as NetworkTable
import calendar


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This chart shows the weekly frequency of having
    at least one watch/warning/advisory (WWA) issued by the Weather Forecast
    Office (top plot) and the overall number of WWA issued for
    that week of the year (bottom plot).  For example, if 10 Tornado Warnings
    were issued during the 30th week of 2014, this would count as 1 year in
    the top plot and 10 events in the bottom plot.  This plot hopefully
    answers the question of which week of the year is most common to get a
    certain WWA type and which week has seen the most WWAs issued.  The plot
    only considers issuance date."""
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True),
        dict(type='phenomena', name='phenomena',
             default='WC', label='Select Watch/Warning Phenomena Type:'),
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

    phenomena = fdict.get('phenomena', 'WC')
    significance = fdict.get('significance', 'W')
    station = fdict.get('station', 'DMX')[:4]

    nt = NetworkTable('WFO')

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    (fig, ax) = plt.subplots(2, 1, sharex=True)

    cursor.execute("""
    with obs as (
        SELECT distinct extract(year from issue) as yr,
        extract(week from issue) as week, eventid from warnings WHERE
        wfo = %s and phenomena = %s and significance = %s
    )
    SELECT yr, week, count(*) from obs GROUP by yr, week ORDER by yr ASC
    """, (station, phenomena, significance))

    weekcount = [0]*53
    eventcount = [0]*53
    years = []
    for row in cursor:
        years.append(row[0])
        weekcount[int(row[1])-1] += 1
        eventcount[int(row[1])-1] += row[2]

    df = pd.DataFrame(dict(week=pd.Series(range(1, 54)),
                           weekcount=pd.Series(weekcount),
                           eventcount=pd.Series(eventcount)))

    if max(weekcount) == 0:
        return "ERROR: No Results Found!"

    ax[0].bar(np.arange(53)*7, weekcount, width=7)
    ax[0].set_title("[%s] NWS %s\n%s %s (%s.%s) Events - %i to %i" % (
        station, nt.sts[station]['name'], vtec._phenDict[phenomena],
        vtec._sigDict[significance], phenomena, significance,
        years[0], years[-1]))
    ax[0].grid()
    ax[0].set_ylabel("Years with 1+ Event")

    ax[1].bar(np.arange(53)*7, eventcount, width=7)
    ax[1].set_ylabel("Total Event Count")
    ax[1].grid()
    ax[1].set_xlabel("Partitioned by Week of the Year")
    ax[1].set_xticks(xticks)
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 366)

    return fig, df
