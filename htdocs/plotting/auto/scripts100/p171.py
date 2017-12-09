"""Distinct VTEC"""
import calendar

import numpy as np
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
import pyiem.nws.vtec as vtec
from pyiem import reference
from pyiem.util import get_autoplot_context, get_dbconn

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

    <p>If you select the state wide option, the totalling is a bit different. A
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
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mpcolors
    import matplotlib.patheffects as PathEffects
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    phenomena = ctx['phenomena']
    significance = ctx['significance']
    opt = ctx['opt']
    state = ctx['state']

    nt = NetworkTable('WFO')
    nt.sts['_ALL'] = {'name': 'All Offices'}

    wfo_limiter = (" and wfo = '%s' "
                   ) % (station if len(station) == 3 else station[1:],)
    if station == '_ALL':
        wfo_limiter = ''
    if opt == 'state':
        wfo_limiter = " and substr(ugc, 1, 2) = '%s'" % (state, )

    df = read_sql("""
        with data as (
            SELECT distinct extract(year from issue) as yr2,
            min(issue) as i, wfo, eventid
            from warnings where phenomena = %s and significance = %s
            """ + wfo_limiter + """
            GROUP by yr2, wfo, eventid)

        SELECT extract(year from i) as yr, extract(month from i) as mo,
        count(*) from data GROUP by yr, mo ORDER by yr, mo ASC
      """, pgconn, params=(phenomena, significance), index_col=None)

    if df.empty:
        raise ValueError("Sorry, no data found!")
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 8))

    minyear = df['yr'].min()
    maxyear = df['yr'].max()
    data = np.zeros((int(maxyear - minyear + 1), 12))
    for _, row in df.iterrows():
        data[int(row['yr'] - minyear), int(row['mo'] - 1)] = row['count']
        txt = ax.text(row['mo'], row['yr'], "%.0f" % (row['count'],),
                      va='center', ha='center', color='white')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="k")])
    cmap = plt.get_cmap('jet')
    cmap.set_under('white')
    maxval = max([df['count'].max(), 11])
    bounds = np.linspace(1, maxval, 10, dtype='i')
    norm = mpcolors.BoundaryNorm(bounds, cmap.N)
    res = ax.imshow(data, extent=[0.5, 12.5, maxyear + 0.5, minyear - 0.5],
                    interpolation='nearest', aspect='auto', norm=norm,
                    cmap=cmap)
    fig.colorbar(res, label='count')
    ax.grid(True)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])

    title = "NWS %s" % (nt.sts[station]['name'], )
    if opt == 'state':
        title = ("NWS Issued for Counties/Zones for State of %s"
                 ) % (reference.state_names[state],)
    title += ("\n%s (%s.%s) Issued by Year,Month"
              ) % (vtec.get_ps_string(phenomena, significance),
                   phenomena, significance)
    ax.set_title(title)

    return fig, df


if __name__ == '__main__':
    plotter(dict(wfo='MOB', network='WFO', phenomena='TO', significance='W'))
