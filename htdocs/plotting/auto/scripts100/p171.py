"""Distinct VTEC"""
import calendar

import numpy as np
from pandas.io.sql import read_sql
import pyiem.nws.vtec as vtec
from pyiem import reference
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'wfo': 'Select by NWS Forecast Office',
         'state': 'Select by State'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This chart displays the monthly number of distinct
    NWS Office issued watch / warning / advisory product. For example, a
    single watch for a dozen counties would only count 1 in this chart. These
    values are based on unofficial archives maintained by the IEM.

    <p>If you select the state wide option, the totaling is a bit different. A
    single watch issued by multiple WFOs would potentially count as more than
    one event in this listing.  Sorry, tough issue to get around.  In the case
    of warnings and advisories, the totals should be good.</p>
    """
    desc['arguments'] = [
        dict(type='select', name='opt', default='wfo',
             options=PDICT, label='Summarize by WFO or State?'),
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True),
        dict(type='state', name='state',
             default='IA', label='Select State:'),
        dict(type='phenomena', name='phenomena',
             default='FF', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import seaborn as sns
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    phenomena = ctx['phenomena']
    significance = ctx['significance']
    opt = ctx['opt']
    state = ctx['state']
    ctx['_nt'].sts['_ALL'] = {'name': 'All Offices'}

    wfo_limiter = (" and wfo = '%s' "
                   ) % (station if len(station) == 3 else station[1:],)
    if station == '_ALL':
        wfo_limiter = ''
    if opt == 'state':
        wfo_limiter = " and substr(ugc, 1, 2) = '%s'" % (state, )

    # NB we added a hack here that may lead to some false positives when events
    # cross over months, sigh, recall the 2017 eventid pain
    df = read_sql("""
        with data as (
            SELECT distinct
            extract(year from issue)::int as yr,
            extract(month from issue)::int as mo, wfo, eventid
            from warnings where phenomena = %s and significance = %s
            """ + wfo_limiter + """
            GROUP by yr, mo, wfo, eventid)

        SELECT yr, mo, count(*) from data GROUP by yr, mo ORDER by yr, mo ASC
      """, pgconn, params=(phenomena, significance), index_col=None)

    if df.empty:
        raise NoDataFound("Sorry, no data found!")
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 8))

    df2 = df.pivot('yr', 'mo', 'count')
    df2 = df2.reindex(
        index=range(df2.index.min(), df2.index.max() + 1),
        columns=range(1, 13))

    title = "NWS %s" % (ctx['_nt'].sts[station]['name'], )
    if opt == 'state':
        title = ("NWS Issued for Counties/Zones for State of %s"
                 ) % (reference.state_names[state],)
    title += ("\n%s (%s.%s) Issued by Year,Month"
              ) % (vtec.get_ps_string(phenomena, significance),
                   phenomena, significance)
    ax.set_title(title)
    sns.heatmap(df2, annot=True, fmt=".0f", linewidths=.5, ax=ax, vmin=1)
    ax.set_xticks(np.arange(12) + 0.5)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_ylabel("Year")
    ax.set_xlabel("Month")

    return fig, df


if __name__ == '__main__':
    plotter(dict(wfo='OUN', network='WFO', phenomena='FG', significance='Y'))
