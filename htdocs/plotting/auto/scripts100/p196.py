"""Plot histogram of alerts by temperature"""

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.nws.vtec import NWS_COLORS
from pyiem.exceptions import NoDataFound

PDICT = {
    'no': 'Consider all calculated Heat Index Values',
    'yes': 'Only consider additive cases, with Heat Index > Temp'
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 3600
    desc['description'] = """This plot presents the frequency that a given
    heat index was under either a Heat Advisory or Extreme Heat Warning. The
    major caveat here is that these alerts tend to be when the heat index
    is elevated for a number of hours straight."""
    desc['arguments'] = [
        dict(type='zstation', name='station', default='AMW', network='IA_ASOS',
             label='Select station:'),
        dict(type="select", options=PDICT, default="no", name="opt",
             label='Should observations be limited?'),
    ]
    return desc


def get_df(ctx):
    """Figure out what data we need to fetch here"""
    ctx['ugc'] = ctx['_nt'].sts[ctx['station']]['ugc_zone']
    pgconn = get_dbconn('postgis')
    events = read_sql("""
        SELECT generate_series(issue, expire, '1 minute'::interval) as valid,
        (phenomena ||'.'|| significance) as vtec
        from warnings WHERE ugc = %s and (
            (phenomena = 'EH' and significance = 'W') or
            (phenomena = 'HT' and significance = 'Y')
        ) ORDER by issue ASC
    """, pgconn, params=(ctx['ugc'], ), index_col='valid')
    if events.empty:
        raise NoDataFound("No Alerts were found for UGC: %s" % (ctx['ugc'], ))
    pgconn = get_dbconn('asos')
    obs = read_sql("""
        SELECT valid, tmpf::int as tmpf, feel
        from alldata where station = %s
        and valid > %s and tmpf > 70 and feel is not null ORDER by valid
    """, pgconn, params=(ctx['station'],
                         str(events.index.values[0])),
                   index_col='valid')
    ctx['title'] = (
        "%s [%s] (%s to %s)\n"
        "Frequency of NWS Heat Headline for %s by Heat Index"
    ) % (ctx['_nt'].sts[ctx['station']]['name'], ctx['station'],
         str(events.index.values[0])[:10], str(obs.index.values[-1])[:10],
         ctx['ugc'])
    if ctx['opt'] == 'yes':
        obs = obs[obs['feel'] > obs['tmpf']]
    obs['feel'] = obs['feel'].round(0)
    res = obs.join(events)
    res.fillna('None', inplace=True)
    counts = res[['feel', 'vtec']].groupby(
        ['feel', 'vtec']).size()
    df = pd.DataFrame(counts)
    df.columns = ['count']
    df.reset_index(inplace=True)
    ctx['df'] = df.pivot(index='feel', columns='vtec', values='count')
    ctx['df'].fillna(0, inplace=True)
    ctx['df']['Total'] = ctx['df'].sum(axis=1)
    for vtec in ['HT.Y', 'EH.W', 'None']:
        if vtec not in ctx['df'].columns:
            ctx['df'][vtec] = 0.
        ctx['df'][vtec+"%"] = ctx['df'][vtec] / ctx['df']['Total'] * 100.


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())

    get_df(ctx)
    (fig, ax) = plt.subplots()

    hty = ctx['df']['HT.Y%']
    ax.bar(ctx['df'].index.values, hty, label='Heat Advisory',
           color=NWS_COLORS['HT.Y'])
    ehw = ctx['df']['EH.W%']
    ax.bar(ctx['df'].index.values, ehw.values, bottom=hty.values,
           label='Extreme Heat Warning',
           color=NWS_COLORS['EH.W'])
    non = ctx['df']['None%']
    ax.bar(ctx['df'].index.values, non, bottom=(hty + ehw).values,
           label='No Headline',
           color='#EEEEEE')
    ax.legend(loc=(-0.03, -0.22), ncol=3)
    ax.set_position([0.1, 0.2, 0.8, 0.7])
    ax.grid(True)
    ax.set_xlabel((
        r"Heat Index $^\circ$F, %s"
        ) % ("All Obs Considered"
             if ctx['opt'] == 'no'
             else "Only Obs with HI > Temp Considered"))
    ax.set_ylabel("Frequency [%]")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_title(ctx['title'])

    return fig, ctx['df']


if __name__ == '__main__':
    plotter(dict(opt='no'))
