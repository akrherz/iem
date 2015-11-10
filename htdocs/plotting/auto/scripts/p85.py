import psycopg2
from pyiem.network import Table as NetworkTable
import calendar
from pandas.io.sql import read_sql

PDICT = {'above': 'At or Above Temperature',
         'below': 'Below Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """Based on IEM archives of METAR reports, this
    application produces the hourly frequency of a temperature at or
    above or below a temperature thresold."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='month', name='month', default=7,
             label='Month:'),
        dict(type='text', name='t', default=80,
             label='Temperature Threshold (F):'),
        dict(type='select', name='dir', default='above',
             label='Threshold Direction:', options=PDICT),
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
    month = int(fdict.get('month', 7))
    thres = int(fdict.get('t', 80))
    mydir = fdict.get('dir', 'above')
    if PDICT.get(mydir) is None:
        return 'Invalid dir provided'

    nt = NetworkTable(network)
    tzname = nt.sts[station]['tzname']

    df = read_sql("""
    WITH data as (
        SELECT valid at time zone %s  + '10 minutes'::interval as v, tmpf
        from alldata where station = %s and tmpf > -90 and tmpf < 150
        and extract(month from valid) = %s)

    SELECT extract(hour from v) as hour,
    sum(case when tmpf::int < %s THEN 1 ELSE 0 END) as below,
    sum(case when tmpf::int >= %s THEN 1 ELSE 0 END) as above,
    count(*) from data
    GROUP by hour ORDER by hour ASC
    """, pgconn, params=(tzname, station, month, thres, thres),
                  index_col='hour')

    df['below_freq'] = df['below'].values.astype('f') / df['count'] * 100.
    df['above_freq'] = df['above'].values.astype('f') / df['count'] * 100.

    freq = df[mydir+"_freq"].values
    hours = df.index.values

    (fig, ax) = plt.subplots(1, 1)
    bars = ax.bar(hours-0.4, freq, fc='blue')
    for i, bar in enumerate(bars):
        ax.text(i, bar.get_height()+3, "%.0f" % (bar.get_height(),),
                ha='center', fontsize=10)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xticklabels(['Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM',
                        '6 PM', '9 PM'])
    ax.grid(True)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Frequency [%]")
    ax.set_xlabel("Hour Timezone: %s" % (tzname,))
    ax.set_xlim(-0.5, 23.5)
    ax.set_title(("%s [%s]\nFrequency of %s Hour, %s: %s$^\circ$F"
                  ) % (nt.sts[station]['name'], station,
                       calendar.month_name[month], PDICT[mydir],
                       thres))

    return fig, df
