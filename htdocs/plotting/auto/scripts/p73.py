import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import datetime
import numpy as np
import math
import pyiem.nws.vtec as vtec
from pyiem.network import Table as NetworkTable
import calendar

PDICT = {'yes': "Limit Plot to Year-to-Date",
         'no': 'Plot Entire Year'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """This chart displays the number of products issued
    by a NWS Office by year for a given watch, warning, or advisory of your
    choice.  These numbers are based on IEM archives and are not official!"""
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True),
        dict(type='select', name='limit', default='no',
             label='End Date Limit to Plot:', options=PDICT),
        dict(type='phenomena', name='phenomena',
             default='FF', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),

    ]
    return d


def plotter(fdict):
    """ Go """
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'DMX')
    limit = fdict.get('limit', 'no')
    phenomena = fdict.get('phenomena', 'FF')
    significance = fdict.get('significance', 'W')

    nt = NetworkTable('WFO')
    nt.sts['_ALL'] = {'name': 'All Offices'}

    lastdoy = 367
    if limit.lower() == 'yes':
        lastdoy = int(datetime.datetime.today().strftime("%j")) + 1

    wfo_limiter = " and wfo = '%s' " % (station,)
    if station == '_ALL':
        wfo_limiter = ''
    doy_limiter = ''
    if limit == 'yes':
        doy_limiter = (" and extract(doy from issue) < "
                       "extract(doy from 'TODAY'::date) ")

    cursor.execute("""
        with data as (
            SELECT distinct extract(year from issue) as yr, wfo, eventid
            from warnings where phenomena = %s and significance = %s
            """ + wfo_limiter + doy_limiter + """)

        SELECT yr, count(*) from data GROUP by yr ORDER by yr ASC
      """, (phenomena, significance))

    years = []
    counts = []
    for row in cursor:
        years.append(row[0])
        counts.append(row[1])

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(np.array(years)-0.4, counts)
    ax.set_xlim(min(years)-0.5, max(years)+0.5)
    ax.grid(True)
    ax.set_ylabel("Yearly Count")
    ax.set_title(("NWS %s\n%s %s (%s.%s) Count"
                  ) % (nt.sts[station]['name'], vtec._phenDict[phenomena],
                       vtec._sigDict[significance], phenomena, significance))
    if limit == 'yes':
        ax.set_xlabel(("thru approximately %s"
                       ) % (datetime.date.today().strftime("%-d %b"), ))

    return fig
