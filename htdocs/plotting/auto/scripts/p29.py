import psycopg2
import pytz
from pyiem.network import Table as NetworkTable
import datetime
import calendar
import numpy as np
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot presents the frequency of a given hourly
    temperature being within the bounds of two temperature thresholds. The
    hour is specified in UTC (Coordinated Universal Time) and observations
    are rounded forward in time such that an observation at :54 after the
    hour is moved to the top of the hour.
    """
    d['data'] = True
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='zhour', name='hour', default=20,
             label='At Time (UTC):'),
        dict(type='text', name='t1', default=70,
             label='Lower Temperature Bound (inclusive):'),
        dict(type='text', name='t2', default=79,
             label='Upper Temperature Bound (inclusive):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    hour = int(fdict.get('hour', 20))
    t1 = int(fdict.get('t1', 70))
    t2 = int(fdict.get('t2', 70))
    nt = NetworkTable(network)

    df = read_sql("""
    WITH obs as (
        SELECT date_trunc('hour', valid) as t,
        round(avg(tmpf)::numeric, 0) as tmp from alldata
        WHERE station = %s and (extract(minute from valid) > 50 or
        extract(minute from valid) = 10) and
        extract(hour from valid at time zone 'UTC') = %s and tmpf is not null
        GROUP by t
    )
    SELECT extract(month from t) as month,
    sum(case when tmp >= %s and tmp <= %s then 1 else 0 end) as hits,
    sum(case when tmp > %s then 1 else 0 end) as above,
    sum(case when tmp < %s then 1 else 0 end) as below,
    count(*) from obs GROUP by month ORDER by month ASC
    """, pgconn, params=(station, hour, t1, t2, t2, t1), index_col='month')
    df['freq'] = df['hits'] / df['count'] * 100.
    df['above_freq'] = df['above'] / df['count'] * 100.
    df['below_freq'] = df['below'] / df['count'] * 100.
    (fig, ax) = plt.subplots(1, 1)
    bars = ax.bar(np.arange(1, 13) - 0.4, df['freq'], fc='tan',
                  label='%s - %s' % (t1, t2), zorder=2)
    ax.scatter(df.index.values, df['above_freq'], marker='s', s=40,
               label="Above %s" % (t2,), color='r', zorder=3)
    ax.scatter(df.index.values, df['below_freq'], marker='s', s=40,
               label="Below %s" % (t1,), color='b', zorder=3)
    for i, bar in enumerate(bars):
        ax.text(i+1, bar.get_height()+3, "%.1f%%" % (bar.get_height(),),
                ha='center', fontsize=12, zorder=4)
    ax.set_xticks(range(0, 13))
    ax.set_xticklabels(calendar.month_abbr)
    ax.grid(True)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Frequency [%]")
    ut = datetime.datetime(2000, 1, 1, hour, 0)
    ut = ut.replace(tzinfo=pytz.timezone("UTC"))
    localt = ut.astimezone(pytz.timezone(nt.sts[station]['tzname']))
    ax.set_xlim(0.5, 12.5)
    ax.set_title(("%s [%s]\nFrequency of %s UTC (%s LST) "
                  "Temp between %s$^\circ$F and %s$^\circ$F"
                  ) % (nt.sts[station]['name'], station, hour,
                       localt.strftime("%-I %p"), t1, t2))
    ax.legend(loc=(0.05, -0.14), ncol=3, fontsize=14)
    pos = ax.get_position()
    ax.set_position([pos.x0, pos.y0 + 0.07, pos.width, pos.height * 0.93])
    return fig, df
