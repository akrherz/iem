"""period between first and last watch"""
import calendar
import datetime

from pandas.io.sql import read_sql
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from pyiem.network import Table as NetworkTable
from pyiem import reference
from pyiem.plot.use_agg import plt
from pyiem.nws import vtec
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'jan1': 'January 1',
         'jul1': 'July 1'}
PDICT2 = {'wfo': 'View by Single NWS Forecast Office',
          'state': 'View by State'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['cache'] = 86400
    desc['description'] = """This chart shows the period between the first
    and last watch, warning, advisory (WWA) issued by an office per year. The
    right hand chart displays the number of unique WWA events issued for
    that year.  The number of events is <strong>not</strong> the combination of
    a WWA product and alerted counties/zones, but an attempt at counting
    distinct WWA. For VTEC, this is the number of unique event ids.
    """
    desc['arguments'] = [
        dict(type='select', name='opt', default='wfo',
             options=PDICT2, label='View by WFO or State?'),
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:'),
        dict(type='state', default='IA', name='state',
             label='Select State:'),
        dict(type='phenomena', name='phenomena',
             default='SV', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),
        dict(type='select', options=PDICT, label='Split the year on date:',
             default='jan1', name='split'),
    ]
    return desc


def plotter(fdict):
    """ Go """

    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station'][:4]
    phenomena = ctx['phenomena']
    significance = ctx['significance']
    split = ctx['split']
    opt = ctx['opt']
    state = ctx['state']

    nt = NetworkTable('WFO')
    wfolimiter = " wfo = '%s' " % (station,)
    if opt == 'state':
        wfolimiter = " substr(ugc, 1, 2) = '%s' " % (state, )

    if split == 'jan1':
        sql = """
            SELECT extract(year from issue)::int as year,
            min(issue at time zone 'UTC') as min_issue,
            max(issue at time zone 'UTC') as max_issue,
            count(distinct wfo || eventid)
            from warnings where """ + wfolimiter + """
            and phenomena = %s and significance = %s
            GROUP by year ORDER by year ASC
        """
    else:
        sql = """
            SELECT
            extract(year from issue - '6 months'::interval)::int as year,
            min(issue at time zone 'UTC') as min_issue,
            max(issue at time zone 'UTC') as max_issue,
            count(distinct wfo || eventid)
            from warnings where """ + wfolimiter + """
            and phenomena = %s and significance = %s
            GROUP by year ORDER by year ASC
        """
    df = read_sql(sql, pgconn, params=(phenomena, significance),
                  index_col=None)
    if df.empty:
        raise NoDataFound("No data found for query")

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

    # allow for small bars when there is just one event
    df.loc[df['enddoy'] == df['startdoy'], 'enddoy'] = df['enddoy'] + 1
    ends = df['enddoy'].values
    starts = df['startdoy'].values
    if len(starts) < 2:
        raise NoDataFound("No Data Found.")
    years = df.index.values

    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes([0.1, 0.1, 0.7, 0.8])

    ax.barh(years, (ends - starts), left=starts, fc='blue', align='center')
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
    title = "[%s] NWS %s" % (station, nt.sts[station]['name'])
    if opt == 'state':
        title = ("NWS Issued Alerts for State of %s"
                 ) % (reference.state_names[state],)
    ax.set_title(("%s\nPeriod between First and Last %s"
                  ) % (title,
                       vtec.get_ps_string(phenomena, significance)))
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
    ax.barh(years, df['count'], fc='blue', align='center')
    ax.set_ylim(years[0]-0.5, years[-1]+0.5)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.grid(True)
    ax.set_xlabel("# Events")
    ax.yaxis.set_major_formatter(xFormatter)
    xloc = plt.MaxNLocator(3)
    ax.xaxis.set_major_locator(xloc)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
