import psycopg2
import pyiem.nws.vtec as vtec
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable
import calendar
from pandas.io.sql import read_sql

PDICT = {'jan1': 'January 1',
         'jul1': 'July 1'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This chart shows the period between the first
    and last watch, warning, advisory (WWA) issued by an office per year. The
    right hand chart displays the number of unique WWA events issued for
    that year.  The number of events is <strong>not</strong> the combination of
    a WWA product and alerted counties/zones, but an attempt at counting
    distinct WWA. For VTEC, this is the number of unique event ids.
    """
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:'),
        dict(type='phenomena', name='phenomena',
             default='SV', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),
        dict(type='select', options=PDICT, label='Split the year on date:',
             default='jan1', name='split'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter

    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')

    station = fdict.get('station', 'DMX')[:4]
    phenomena = fdict.get('phenomena', 'SV')
    significance = fdict.get('significance', 'W')
    split = fdict.get('split', 'jan1')

    nt = NetworkTable('WFO')

    if split == 'jan1':
        sql = """SELECT extract(year from issue)::int as year,
        min(issue at time zone 'UTC') as min_issue,
        max(issue at time zone 'UTC') as max_issue,
        count(distinct eventid)
        from warnings where wfo = %s and phenomena = %s and significance = %s
        and issue is not null
        GROUP by year ORDER by year ASC"""
    else:
        sql = """SELECT
        extract(year from issue - '6 months'::interval)::int as year,
        min(issue at time zone 'UTC') as min_issue,
        max(issue at time zone 'UTC') as max_issue,
        count(distinct eventid)
        from warnings where wfo = %s and phenomena = %s and significance = %s
        and issue is not null
        GROUP by year ORDER by year ASC"""
    df = read_sql(sql, pgconn, params=(station, phenomena, significance),
                  index_col=None)

    # Since many VTEC events start in 2005, we should not trust any
    # data that has its first year in 2005
    if df['year'].min() == 2005:
        df = df[df['year'] > 2005]

    def myfunc(row):
        year = row[0]
        valid = row[1]
        if year == valid.year:
            return int(valid.strftime("%j"))
        else:
            days = (datetime.date(year+1, 1, 1) -
                    datetime.date(year, 1, 1)).days
            return int(valid.strftime("%j")) + days
    df['startdoy'] = df[['year', 'min_issue']].apply(myfunc, axis=1)
    df['enddoy'] = df[['year', 'max_issue']].apply(myfunc, axis=1)
    df.set_index('year', inplace=True)

    ends = df['enddoy'].values
    starts = df['startdoy'].values
    years = df.index.values

    fig = plt.Figure()
    ax = plt.axes([0.1, 0.1, 0.7, 0.8])

    ax.barh(years-0.4, (ends - starts), left=starts, fc='blue')
    ax.axvline(np.average(starts[:-1]), lw=2, color='red')
    ax.axvline(np.average(ends[:-1]), lw=2, color='red')
    ax.set_xlabel(("Avg Start Date: %s, End Date: %s"
                   ) % (
     (datetime.date(2000, 1, 1) +
      datetime.timedelta(days=int(np.average(starts[:-1])))).strftime(
                                                                "%-d %b"),
     (datetime.date(2000, 1, 1) +
      datetime.timedelta(days=int(np.average(ends[:-1])))).strftime(
                                                                "%-d %b")),
                  color='red')
    ax.set_title(("[%s] NWS %s\nPeriod between First and Last %s %s"
                  ) % (station, nt.sts[station]['name'],
                       vtec._phenDict[phenomena],
                       vtec._sigDict[significance]))
    ax.grid()
    days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274,
            305, 335]
    days = days + [x + 365 for x in days]
    ax.set_xticks(days)
    ax.set_xticklabels(calendar.month_abbr[1:] + calendar.month_abbr[1:])
    ax.set_xlim(df['startdoy'].min() - 10, df['enddoy'].max() + 10)
    ax.set_ylabel("Year")
    ax.set_ylim(years[0]-0.5, years[-1]+0.5)
    xFormatter = FormatStrFormatter('%d')
    ax.yaxis.set_major_formatter(xFormatter)

    ax = plt.axes([0.82, 0.1, 0.13, 0.8])
    ax.barh(years-0.4, df['count'], fc='blue')
    ax.set_ylim(years[0]-0.5, years[-1]+0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Events")
    ax.yaxis.set_major_formatter(xFormatter)
    xloc = plt.MaxNLocator(3)
    ax.xaxis.set_major_locator(xloc)

    return fig, df
