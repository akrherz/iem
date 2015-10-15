import psycopg2
import datetime
import pyiem.nws.vtec as vtec
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql

PDICT = {'yes': "Limit Plot to Year-to-Date",
         'no': 'Plot Entire Year'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
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
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')

    station = fdict.get('station', 'DMX')
    limit = fdict.get('limit', 'no')
    phenomena = fdict.get('phenomena', 'FF')
    significance = fdict.get('significance', 'W')

    nt = NetworkTable('WFO')
    nt.sts['_ALL'] = {'name': 'All Offices'}

    wfo_limiter = (" and wfo = '%s' "
                   ) % (station if len(station) == 3 else station[1:],)
    if station == '_ALL':
        wfo_limiter = ''
    doy_limiter = ''
    if limit.lower() == 'yes':
        doy_limiter = (" and extract(doy from issue) < "
                       "extract(doy from 'TODAY'::date) ")

    df = read_sql("""
        with data as (
            SELECT distinct extract(year from issue) as yr, wfo, eventid
            from warnings where phenomena = %s and significance = %s
            """ + wfo_limiter + doy_limiter + """)

        SELECT yr, count(*) from data GROUP by yr ORDER by yr ASC
      """, pgconn, params=(phenomena, significance))

    if len(df.index) == 0:
        return("Sorry, no data found!")

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df['yr']-0.4, df['count'])
    ax.set_xlim(df['yr'].min()-0.5, df['yr'].max()+0.5)
    ax.grid(True)
    ax.set_ylabel("Yearly Count")
    ax.set_title(("NWS %s\n%s %s (%s.%s) Count"
                  ) % (nt.sts[station]['name'], vtec._phenDict[phenomena],
                       vtec._sigDict[significance], phenomena, significance))
    if limit == 'yes':
        ax.set_xlabel(("thru approximately %s"
                       ) % (datetime.date.today().strftime("%-d %b"), ))

    return fig, df
