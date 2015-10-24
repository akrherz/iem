import psycopg2
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import datetime
import pytz
from pyiem.nws import vtec
from pyiem.plot import MapPlot


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This application generates a map of the number of
    VTEC encoded Watch, Warning,
     and Advisory (WWA) events by NWS Forecast Office for a time period of
     your choice. The archive of products goes back to October 2005.
     Note: Not all VTEC products go back to 2005.
     You can optionally plot up to 4 different VTEC phenomena and significance
     types."""
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    d['arguments'] = [
        dict(type='datetime', name='sdate',
             default=jan1.strftime("%Y/%m/%d 0000"),
             label='Start Date / Time (UTC, inclusive):', min="2005/01/01"),
        dict(type='datetime', name='edate',
             default=today.strftime("%Y/%m/%d 0000"),
             label='End Date / Time (UTC):', min="2005/01/01"),
        dict(type='vtec_ps', name='v1', default='UNUSED',
             label='VTEC Phenomena and Significance 1'),
        dict(type='vtec_ps', name='v2', default='UNUSED', optional=True,
             label='VTEC Phenomena and Significance 2'),
        dict(type='vtec_ps', name='v3', default='UNUSED', optional=True,
             label='VTEC Phenomena and Significance 3'),
        dict(type='vtec_ps', name='v4', default='UNUSED', optional=True,
             label='VTEC Phenomena and Significance 4'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')

    sts = datetime.datetime.strptime(fdict.get('sdate', '2015-01-01 0000'),
                                     '%Y-%m-%d %H%M')
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    ets = datetime.datetime.strptime(fdict.get('edate', '2015-02-01 0000'),
                                     '%Y-%m-%d %H%M')
    ets = ets.replace(tzinfo=pytz.timezone("UTC"))
    p1 = fdict.get('phenomenav1', 'SV')[:2]
    p2 = fdict.get('phenomenav2', '  ')[:2]
    p3 = fdict.get('phenomenav3', '  ')[:2]
    p4 = fdict.get('phenomenav4', '  ')[:2]
    phenomena = []
    for p in [p1, p2, p3, p4]:
        if p != '  ':
            phenomena.append(p)
    s1 = fdict.get('significancev1', 'W')[0]
    s2 = fdict.get('significancev2', ' ')[0]
    s3 = fdict.get('significancev3', ' ')[0]
    s4 = fdict.get('significancev4', ' ')[0]
    significance = []
    for s in [s1, s2, s3, s4]:
        if s != '  ':
            significance.append(s)

    pstr = []
    subtitle = ""
    title = ""
    for p, s in zip(phenomena, significance):
        pstr.append("(phenomena = '%s' and significance = '%s')" % (p, s))
        subtitle += "%s.%s " % (p, s)
        title += "%s %s" % (vtec._phenDict.get(p, p),
                            vtec._sigDict.get(s, s))
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
    bins = [0, 1, 3, 5, 10, 20, 35, 50, 75, 100, 150, 200, 250,
            500, 750, 1000]
    if maxv > 1000:
        bins = [0, 1, 5, 10, 50, 100, 150, 200, 250,
                500, 750, 1000, 1250, 1500, 2000]

    p = MapPlot(sector='nws', axisbg='white',
                title='%s Counts by NWS Office' % (title,),
                subtitle=('Valid %s - %s UTC, based on VTEC: %s'
                          ) % (sts.strftime("%d %b %Y %H:%M"),
                               ets.strftime("%d %b %Y %H:%M"),
                               subtitle))
    p.fill_cwas(df2, bins=bins, ilabel=True)

    return p.fig, df

if __name__ == '__main__':
    plotter(dict())
