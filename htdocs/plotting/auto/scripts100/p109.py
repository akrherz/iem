"""WFO VTEC counts in a map"""
import datetime

from pandas.io.sql import read_sql
import pytz
from pyiem.network import Table as NetworkTable
from pyiem.nws import vtec
from pyiem.plot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application generates a map of the number of
    VTEC encoded Watch, Warning,
     and Advisory (WWA) events by NWS Forecast Office for a time period of
     your choice. The archive of products goes back to October 2005.
     Note: Not all VTEC products go back to 2005.
     You can optionally plot up to 4 different VTEC phenomena and significance
     types."""
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
        dict(type='vtec_ps', name='v1', default='UNUSED',
             label='VTEC Phenomena and Significance 1'),
        dict(type='vtec_ps', name='v2', default='UNUSED', optional=True,
             label='VTEC Phenomena and Significance 2'),
        dict(type='vtec_ps', name='v3', default='UNUSED', optional=True,
             label='VTEC Phenomena and Significance 3'),
        dict(type='vtec_ps', name='v4', default='UNUSED', optional=True,
             label='VTEC Phenomena and Significance 4'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx['sdate']
    sts = sts.replace(tzinfo=pytz.utc)
    ets = ctx['edate']
    ets = ets.replace(tzinfo=pytz.utc)
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

    nt = NetworkTable("WFO")
    for sid in nt.sts:
        sid = sid[-3:]
        if sid not in df2:
            df2[sid] = 0
    maxv = df2.max()
    bins = [0, 1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 200]
    if maxv > 200:
        bins = [0, 1, 3, 5, 10, 20, 35, 50, 75, 100, 150, 200, 250,
                500, 750, 1000]
    elif maxv > 1000:
        bins = [0, 1, 5, 10, 50, 100, 150, 200, 250,
                500, 750, 1000, 1250, 1500, 2000]

    mp = MapPlot(sector='nws', axisbg='white',
                 title='%s Counts by NWS Office' % (title,),
                 subtitle=('Valid %s - %s UTC, based on VTEC: %s'
                           ) % (sts.strftime("%d %b %Y %H:%M"),
                                ets.strftime("%d %b %Y %H:%M"),
                                subtitle))
    mp.fill_cwas(df2, bins=bins, ilabel=True)

    return mp.fig, df


if __name__ == '__main__':
    plotter(dict())
