"""WFO VTEC counts on a map."""
from collections import OrderedDict
import datetime

from pandas.io.sql import read_sql
import numpy as np
import pytz
from pyiem.nws import vtec
from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable  # This is needed.
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = OrderedDict((
    ('count', "Event Count"),
    ('days', "Days with 1+ Events"),
    ('tpercent', "Percent of Time"),
))


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application generates per WFO maps of VTEC
    event counts.  The current three available metrics are:<br />
    <ul>
        <li><strong>Event Count</strong>: The number of distinct VTEC events.
        A distinct event is simply the usage of one VTEC event identifier.</li>
        <li><strong>Days with 1+ Events</strong>: This is the number of days
        within the period of interest that had at least one VTEC event. A day
        is defined within the US Central Time Zone.  If one event crosses
        midnight, this would count as two days.</li>
        <li><strong>Percent of Time</strong>: This is the temporal coverage
        percentage within the period of interest.  Rewording, what percentage
        of the time was at least one event active.</li>
    </ul></p>

    <p>Note that various VTEC events have differenting start periods of record.
    Most products go back to October 2005.</p>
    """
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    desc['arguments'] = [
        dict(type='datetime', name='sdate',
             default=jan1.strftime("%Y/%m/%d 0000"),
             label='Start Date / Time (UTC, inclusive):',
             min="2005/01/01 0000"),
        dict(type='datetime', name='edate',
             default=today.strftime("%Y/%m/%d 0000"),
             label='End Date / Time (UTC):', min="2005/01/01 0000"),
        dict(type='select', name='var', default='count', options=PDICT,
             label='Which metric to plot:'),
        dict(type='vtec_ps', name='v1', default='SV.W',
             label='VTEC Phenomena and Significance 1'),
        dict(type='vtec_ps', name='v2', default='SV.W', optional=True,
             label='VTEC Phenomena and Significance 2'),
        dict(type='vtec_ps', name='v3', default='SV.W', optional=True,
             label='VTEC Phenomena and Significance 3'),
        dict(type='vtec_ps', name='v4', default='SV.W', optional=True,
             label='VTEC Phenomena and Significance 4'),
        dict(type='cmap', name='cmap', default='jet', label='Color Ramp:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx['sdate']
    sts = sts.replace(tzinfo=pytz.UTC)
    ets = ctx['edate']
    ets = ets.replace(tzinfo=pytz.UTC)
    p1 = ctx['phenomenav1']
    p2 = ctx['phenomenav2']
    p3 = ctx['phenomenav3']
    p4 = ctx['phenomenav4']
    varname = ctx['var']
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
    subtitle = ""
    title = ""
    for p, s in zip(phenomena, significance):
        pstr.append("(phenomena = '%s' and significance = '%s')" % (p, s))
        subtitle += "%s.%s " % (p, s)
        title += vtec.get_ps_string(p, s)
    if len(phenomena) > 1:
        title = "VTEC Unique Event"
    pstr = " or ".join(pstr)
    pstr = "(%s)" % (pstr,)
    cmap = plt.get_cmap(ctx['cmap'])

    if varname == 'count':
        df = read_sql("""
    with total as (
    select distinct wfo, extract(year from issue at time zone 'UTC') as year,
    phenomena, significance, eventid from warnings
    where """ + pstr + """ and
    issue >= %s and issue < %s
    )

    SELECT wfo, phenomena, significance, year, count(*) from total
    GROUP by wfo, phenomena, significance, year
        """, pgconn, params=(sts, ets))

        df2 = df.groupby('wfo')['count'].sum()
        maxv = df2.max()
        bins = [0, 1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 200]
        if maxv > 5000:
            bins = [0, 5, 10, 50, 100, 250,
                    500, 750, 1000, 1500, 2000, 3000, 5000, 7500, 10000]
        elif maxv > 1000:
            bins = [0, 1, 5, 10, 50, 100, 150, 200, 250,
                    500, 750, 1000, 1250, 1500, 2000]
        elif maxv > 200:
            bins = [0, 1, 3, 5, 10, 20, 35, 50, 75, 100, 150, 200, 250,
                    500, 750, 1000]
        units = 'Count'
        lformat = '%.0f'
    elif varname == 'days':
        df = read_sql("""
        WITH data as (
            SELECT distinct wfo, generate_series(greatest(issue, %s),
            least(expire, %s), '1 minute'::interval) as ts from warnings
            WHERE issue > %s and expire < %s and """ + pstr + """
        ), agg as (
            SELECT distinct wfo, date(ts) from data
        )
        select wfo, count(*) as days from agg
        GROUP by wfo ORDER by days DESC
        """, pgconn, params=(sts, ets, sts - datetime.timedelta(days=90),
                             ets + datetime.timedelta(days=90)
                             ), index_col='wfo')

        df2 = df['days']
        if df2.max() < 10:
            bins = list(range(1, 11, 1))
        else:
            bins = np.linspace(1, df['days'].max() + 11, 10, dtype='i')
        units = 'Days'
        lformat = '%.0f'
        cmap.set_under('white')
        cmap.set_over('#EEEEEE')
    else:
        total_minutes = (ets - sts).total_seconds() / 60.
        df = read_sql("""
        WITH data as (
            SELECT distinct wfo, generate_series(greatest(issue, %s),
            least(expire, %s), '1 minute'::interval) as ts from warnings
            WHERE issue > %s and expire < %s and """ + pstr + """
        )
        select wfo, count(*) / %s * 100. as tpercent from data
        GROUP by wfo ORDER by tpercent DESC
        """, pgconn, params=(sts, ets, sts - datetime.timedelta(days=90),
                             ets + datetime.timedelta(days=90),
                             total_minutes), index_col='wfo')

        df2 = df['tpercent']
        bins = list(range(0, 101, 10))
        if df2.max() < 5:
            bins = np.arange(0, 5.1, 0.5)
        elif df2.max() < 10:
            bins = list(range(0, 11, 1))
        units = 'Percent'
        lformat = '%.1f'

    nt = NetworkTable("WFO")
    for sid in nt.sts:
        sid = sid[-3:]
        if sid not in df2:
            df2[sid] = 0

    mp = MapPlot(sector='nws', axisbg='white',
                 title='%s %s by NWS Office' % (title, PDICT[varname]),
                 subtitle=('Valid %s - %s UTC, based on VTEC: %s'
                           ) % (sts.strftime("%d %b %Y %H:%M"),
                                ets.strftime("%d %b %Y %H:%M"),
                                subtitle))
    mp.fill_cwas(
        df2, bins=bins, ilabel=True, units=units, lblformat=lformat,
        cmap=cmap)

    return mp.fig, df


if __name__ == '__main__':
    plotter({'var': 'tpercent', 'phenomenav1': 'SV', 'significancev1': 'W'})
