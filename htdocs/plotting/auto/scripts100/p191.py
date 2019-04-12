"""VTEC Products issued by date"""
import datetime

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.nws import vtec
from pyiem.plot import calendar_plot
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {'yes': 'Colorize Cells in Chart',
         'no': 'Just plot values please'}
PDICT2 = {'wfo': 'Summarize by Selected WFO',
          'state': 'Summarize by Selected State'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application presents a calendar of daily
    counts of the number of watch, warning, advisories issued by day.  This
    accounting is based on the initial issuance date of a given VTEC phenomena
    and significance by event identifier.  So a single Winter Storm Watch
    for 40 zones, would only count as 1 event for this chart.  Dates are
    computed in the local time zone of the issuance forecast office in the
    case of a single office and in Central Time for the case of all offices of
    plotting a given state.

    <p>You can also generate this plot considering "ALL" NWS Offices, when
    doing so the time zone used to compute the calendar dates is US Central.
    """
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    desc['arguments'] = [
        dict(type='date', name='sdate',
             default=jan1.strftime("%Y/%m/%d"),
             label='Start Date (inclusive):',
             min="1986/01/01"),
        dict(type='date', name='edate',
             default=today.strftime("%Y/%m/%d"),
             label='End Date (inclusive):',
             min="1986/01/01"),
        dict(type='select', name='w', options=PDICT2, default='wfo',
             label='How to summarize data:'),
        dict(type='networkselect', name='wfo', network='WFO', all=True,
             default='DMX', label='Select WFO (when appropriate):'),
        dict(type='state', name='state',
             default='IA', label='Select State (when appropriate):'),
        dict(type='select', name='heatmap', options=PDICT, default='yes',
             label='Colorize calendar cells based on values?'),
        dict(type='vtec_ps', name='v1', default='SV.W',
             label='VTEC Phenomena and Significance 1'),
        dict(type='vtec_ps', name='v2', default='SV.W', optional=True,
             label='VTEC Phenomena and Significance 2'),
        dict(type='vtec_ps', name='v3', default='SV.W', optional=True,
             label='VTEC Phenomena and Significance 3'),
        dict(type='vtec_ps', name='v4', default='SV.W', optional=True,
             label='VTEC Phenomena and Significance 4'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx['sdate']
    ets = ctx['edate']
    wfo = ctx['wfo']
    p1 = ctx['phenomenav1']
    p2 = ctx['phenomenav2']
    p3 = ctx['phenomenav3']
    p4 = ctx['phenomenav4']
    phenomena = []
    for p in [p1, p2, p3, p4]:
        if p is not None:
            phenomena.append(p[:2])
    s1 = ctx['significancev1']
    s2 = ctx['significancev2']
    s3 = ctx['significancev3']
    s4 = ctx['significancev4']
    significance = []
    for s in [s1, s2, s3, s4]:
        if s is not None:
            significance.append(s[0])

    pstr = []
    title = ""
    for i, (p, s) in enumerate(zip(phenomena, significance)):
        pstr.append("(phenomena = '%s' and significance = '%s')" % (p, s))
        if i == 2:
            title += "\n"
        title += "%s %s.%s, " % (vtec.get_ps_string(p, s), p, s)
    pstr = " or ".join(pstr)
    pstr = "(%s)" % (pstr,)

    if ctx['w'] == 'wfo':
        nt = NetworkTable("WFO")
        nt.sts['_ALL'] = {'name': 'All Offices', 'tzname': 'America/Chicago'}
        wfo_limiter = (" and wfo = '%s' "
                       ) % (wfo if len(wfo) == 3 else wfo[1:],)
        if wfo == '_ALL':
            wfo_limiter = ''
        tzname = nt.sts[wfo]['tzname']
    else:
        wfo_limiter = " and substr(ugc, 1, 2) = '%s' " % (ctx['state'], )
        tzname = 'America/Chicago'

    df = read_sql("""
with events as (
  select wfo, min(issue at time zone %s) as localissue,
  extract(year from issue) as year,
  phenomena, significance, eventid from warnings
  where """ + pstr + """ """ + wfo_limiter + """ and
  issue >= %s and issue < %s GROUP by wfo, year, phenomena, significance,
  eventid
)

SELECT date(localissue), count(*) from events GROUP by date(localissue)
    """, pgconn, params=(tzname,
                         sts - datetime.timedelta(days=2),
                         ets + datetime.timedelta(days=2)), index_col='date')

    data = {}
    now = sts
    while now <= ets:
        data[now] = {'val': 0}
        now += datetime.timedelta(days=1)
    for date, row in df.iterrows():
        data[date] = {'val': row['count']}
    fig = calendar_plot(sts, ets, data, heatmap=(ctx['heatmap'] == 'yes'))
    if ctx['w'] == 'wfo':
        title2 = "NWS %s [%s]" % (nt.sts[wfo]['name'], wfo)
        if wfo == '_ALL':
            title2 = "All NWS Offices"
    else:
        title2 = state_names[ctx['state']]
    fig.text(0.5, 0.95,
             ("Number of VTEC Events for %s by Local Calendar Date"
              "\nValid %s - %s for %s"
              ) % (title2,
                   sts.strftime("%d %b %Y"), ets.strftime("%d %b %Y"),
                   title),
             ha='center', va='center')

    return fig, df


if __name__ == '__main__':
    plotter(dict(phenomenav1='FG', significancev1='Y', sdate='2017-01-01',
                 edate='2017-12-31', wfo='OUN'))
