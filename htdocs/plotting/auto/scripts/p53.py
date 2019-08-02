"""Binned"""
import datetime
import calendar

import psycopg2.extras
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {'tmpf': 'Air Temperature',
         'dwpf': 'Dew Point Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['cache'] = 86400
    desc['description'] = """This plot is a histogram of observed temperatures
    placed into five range bins of your choice.  The plot attempts to answer
    the question of how often is the air temperature within a certain range
    during a certain time of the year.  The data for this plot is partitioned
    by week of the year."""
    desc['data'] = True
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', options=PDICT, default='tmpf', name='var',
             label='Select temperature to plot:'),
        dict(type='int', name='t1', default=0,
             label='Temperature Threshold #1 (lowest)'),
        dict(type='int', name='t2', default=32,
             label='Temperature Threshold #2'),
        dict(type='int', name='t3', default=50,
             label='Temperature Threshold #3'),
        dict(type='int', name='t4', default=70,
             label='Temperature Threshold #4'),
        dict(type='int', name='t5', default=90,
             label='Temperature Threshold #5 (highest)'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['zstation']
    t1 = ctx['t1']
    t2 = ctx['t2']
    t3 = ctx['t3']
    t4 = ctx['t4']
    t5 = ctx['t5']
    v = ctx['var']

    cursor.execute("""
        SELECT extract(week from valid) as w,
        sum(case when """ + v + """::int < %s then 1 else 0 end),
        sum(case when """ + v + """::int < %s then 1 else 0 end),
        sum(case when """ + v + """::int < %s then 1 else 0 end),
        sum(case when """ + v + """::int < %s then 1 else 0 end),
        sum(case when """ + v + """::int < %s then 1 else 0 end),
        count(*)
        from alldata where station = %s and """ + v + """ is not null
        and extract(minute  from valid  - '1 minute'::interval) > 49
        and report_type = 2
        GROUP by w ORDER by w ASC
    """, (t1, t2, t3, t4, t5, station))
    weeks = []
    d1 = []
    d2 = []
    d3 = []
    d4 = []
    d5 = []
    d6 = []
    for row in cursor:
        weeks.append(row[0]-1)
        d1.append(float(row[1]) / float(row[6]) * 100.)
        d2.append(float(row[2]) / float(row[6]) * 100.)
        d3.append(float(row[3]) / float(row[6]) * 100.)
        d4.append(float(row[4]) / float(row[6]) * 100.)
        d5.append(float(row[5]) / float(row[6]) * 100.)
        d6.append(100.)

    df = pd.DataFrame(dict(week=pd.Series(weeks),
                           d1=pd.Series(d1),
                           d2=pd.Series(d2),
                           d3=pd.Series(d3),
                           d4=pd.Series(d4),
                           d5=pd.Series(d5)))
    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(weeks, d6, width=1, fc='red', ec='None',
           label='%s & Above' % (t5,))
    ax.bar(weeks, d5, width=1, fc='tan', ec='None',
           label='%s-%s' % (t4, t5 - 1))
    ax.bar(weeks, d4, width=1, fc='yellow', ec='None',
           label='%s-%s' % (t3, t4 - 1))
    ax.bar(weeks, d3, width=1, fc='green', ec='None',
           label='%s-%s' % (t2, t3 - 1))
    ax.bar(weeks, d2, width=1, fc='blue', ec='None',
           label='%s-%s' % (t1, t2 - 1))
    ax.bar(weeks, d1, width=1, fc='purple', ec='None',
           label='Below %s' % (t1))

    ax.grid(True, zorder=11)
    ab = ctx['_nt'].sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(("%s [%s]\n"
                  r"Hourly %s ($^\circ$F) Frequencies (%s-%s)"
                  ) % (ctx['_nt'].sts[station]['name'], station,
                       PDICT[v], ab.year,
                       datetime.datetime.now().year))
    ax.set_ylabel("Frequency [%]")

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
                     box.width, box.height * 0.8])

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
              fancybox=True, shadow=True, ncol=3, scatterpoints=1, fontsize=12)

    return fig, df


if __name__ == '__main__':
    plotter(dict())
