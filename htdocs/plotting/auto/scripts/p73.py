"""Simple plot of number of WAWA"""
import datetime

from pandas.io.sql import read_sql
from matplotlib.ticker import MaxNLocator
import pyiem.nws.vtec as vtec
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'yes': "Limit Plot to Year-to-Date",
         'no': 'Plot Entire Year'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This chart displays the number of products issued
    by a NWS Office by year for a given watch, warning, or advisory of your
    choice.  These numbers are based on IEM archives and are not official!"""
    desc['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True),
        dict(type='select', name='limit', default='no',
             label='End Date Limit to Plot:', options=PDICT),
        dict(type='phenomena', name='phenomena',
             default='FF', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),

    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    limit = ctx['limit']
    phenomena = ctx['phenomena']
    significance = ctx['significance']

    nt = NetworkTable('WFO')
    nt.sts['_ALL'] = {'name': 'All Offices'}
    if station not in nt.sts:
        raise NoDataFound("Station metadata unknown.")

    wfo_limiter = (" and wfo = '%s' "
                   ) % (station if len(station) == 3 else station[1:],)
    if station == '_ALL':
        wfo_limiter = ''
    doy_limiter = ''
    title = "Entire Year"
    if limit.lower() == 'yes':
        title = "thru ~%s" % (datetime.date.today().strftime("%-d %b"),)
        doy_limiter = (" and extract(doy from issue) <= "
                       "extract(doy from 'TODAY'::date) ")

    df = read_sql("""
        with data as (
            SELECT distinct extract(year from issue)::int as yr, wfo, eventid
            from warnings where phenomena = %s and significance = %s
            """ + wfo_limiter + doy_limiter + """)

        SELECT yr, count(*) from data GROUP by yr ORDER by yr ASC
      """, pgconn, params=(phenomena, significance))
    if df.empty:
        raise NoDataFound("Sorry, no data found!")

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df['yr'], df['count'], align='center')
    ax.set_xlim(df['yr'].min()-0.5, df['yr'].max()+0.5)
    ax.grid(True)
    ax.set_ylabel("Yearly Count")
    ax.set_title(("NWS %s [%s]\n%s (%s.%s) Count"
                  ) % (nt.sts[station]['name'], title,
                       vtec.get_ps_string(phenomena, significance),
                       phenomena, significance))
    if limit == 'yes':
        ax.set_xlabel(("thru approximately %s"
                       ) % (datetime.date.today().strftime("%-d %b"), ))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig, df


if __name__ == '__main__':
    plotter(dict())
