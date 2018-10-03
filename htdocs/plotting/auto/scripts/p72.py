"""histogram of issuance time"""

from pandas.io.sql import read_sql
from pyiem.nws import vtec
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['cache'] = 86400
    desc['data'] = True
    desc['description'] = """This chart presents a histogram of the Watch,
    Warning, Advisory valid time.  This is the time period between the
    issuance and final expiration time of a given event.  An individual event
    is one Valid Time Event Code (VTEC) event identifier.  For example, a
    Winter Storm Watch for 30 counties would only count as one event in this
    analysis.

    <p>If an individual event goes for more than 24 hours, the event is
    capped at a 24 hour duration for the purposes of this analysis.  Events
    like Flood Warnings are prime examples of this.
    """
    desc['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:'),
        dict(type='phenomena', name='phenomena',
             default='WC', label='Select Watch/Warning Phenomena Type:'),
        dict(type='significance', name='significance',
             default='W', label='Select Watch/Warning Significance Level:'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('postgis')
    ctx = get_autoplot_context(fdict, get_description())

    wfo = ctx['station']
    phenomena = ctx['phenomena']
    significance = ctx['significance']

    nt = NetworkTable("WFO")

    (fig, ax) = plt.subplots(1, 1)

    tzname = nt.sts[wfo]['tzname']
    df = read_sql("""
    WITH data as (
     SELECT extract(year from issue) as yr, eventid,
     min(issue at time zone %s) as minissue,
     max(expire at time zone %s) as maxexpire from warnings WHERE
     phenomena = %s and significance = %s
     and wfo = %s GROUP by yr, eventid),
    events as (select count(*) from data),
    timedomain as (
        SELECT generate_series(minissue,
            least(maxexpire, minissue + '24 hours'::interval)
            , '1 minute'::interval)
        as ts from data
    ),
    data2 as (
        SELECT extract(hour from ts)::int * 60 + extract(minute from ts)::int
        as minute, count(*) from timedomain
        GROUP by minute ORDER by minute ASC)
    select d.minute, d.count, e.count as total from data2 d, events e
    """, pgconn, params=(tzname, tzname, phenomena, significance, wfo),
                  index_col='minute')
    if df.empty:
        raise ValueError("No Results Found")
    df['frequency'] = df['count'] / df['total'] * 100.
    ax.bar(df.index.values, df['frequency'].values, ec='b', fc='b',
           align='center')
    ax.grid()
    if df['frequency'].max() > 70:
        ax.set_ylim(0, 101)
    ax.set_xticks(range(0, 25 * 60, 60))
    ax.set_xlim(-0.5, 24 * 60 + 1)
    ax.set_xticklabels(["Mid", "", "", "3 AM", "", "", "6 AM", "", "", '9 AM',
                        "", "", "Noon", "", "", "3 PM", "", "", "6 PM",
                        "", "", "9 PM", "", "", "Mid"])
    ax.set_xlabel("Timezone: %s (Daylight or Standard)" % (tzname,))
    ax.set_ylabel("Percentage [%%] out of %.0f Events" % (df['total'].max(), ))
    ax.set_title(("[%s] %s :: Time of Day Frequency\n%s (%s.%s)"
                  ) % (wfo, nt.sts[wfo]['name'],
                       vtec.get_ps_string(phenomena, significance),
                       phenomena, significance))

    return fig, df


if __name__ == '__main__':
    plotter(dict())
