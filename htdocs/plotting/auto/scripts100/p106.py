"""hourly histogram on days"""
import datetime
from collections import OrderedDict

import psycopg2.extras
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {'tmpf_above': 'Temperature At or Above Threshold (F)',
         'tmpf_below': 'Temperature Below Threshold (F)'}

MDICT = OrderedDict([
        ('all', 'No Month/Time Limit'),
        ('spring', 'Spring (MAM)'),
        ('fall', 'Fall (SON)'),
        ('winter', 'Winter (DJF)'),
        ('summer', 'Summer (JJA)'),
        ('jan', 'January'),
        ('feb', 'February'),
        ('mar', 'March'),
        ('apr', 'April'),
        ('may', 'May'),
        ('jun', 'June'),
        ('jul', 'July'),
        ('aug', 'August'),
        ('sep', 'September'),
        ('oct', 'October'),
        ('nov', 'November'),
        ('dec', 'December')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['description'] = """
    This plot displays hourly temperature distributions
    for a given time period and temperature threshold of your choice.  The
    temperature threshold is for one or more exceedences for the day.
    """
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:', network='IA_ASOS'),
        dict(type='select', name='opt', default='tmpf_above',
             label='Criterion?', options=PDICT),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='int', name='threshold', default='80',
             label='Temperature Threshold (F):')
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('asos')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    threshold = ctx['threshold']
    opt = ctx['opt']
    month = ctx['month']

    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    if opt == 'tmpf_above':
        limiter = "round(tmpf::numeric,0) >= %s" % (threshold,)
    else:
        limiter = "round(tmpf::numeric,0) < %s" % (threshold,)

    cursor.execute("""
        WITH obs as (
            SELECT valid, tmpf from alldata WHERE
            station = %s and extract(month from valid) in %s and tmpf > -80
        ),
        events as (
            SELECT distinct date(valid at time zone %s) from obs
            WHERE """ + limiter + """)
     SELECT valid at time zone %s + '10 minutes'::interval, tmpf
     from obs a JOIN events e on
     (date(a.valid at time zone %s) = e.date)
    """, (station, tuple(months), ctx['_nt'].sts[station]['tzname'],
          ctx['_nt'].sts[station]['tzname'],
          ctx['_nt'].sts[station]['tzname']))
    data = []
    for _ in range(24):
        data.append([])
    for row in cursor:
        data[row[0].hour].append(row[1])

    fig, ax = plt.subplots(1, 1)
    ax.boxplot(data)
    ax.grid(True)
    ax.set_title("%s [%s] Hourly Temps on\nDays (%s) with %s %.0f" % (
        ctx['_nt'].sts[station]['name'], station, month.capitalize(),
        PDICT[opt], threshold))
    ax.set_ylabel(r"Temperature $^\circ$F")
    ax.set_xlabel("Local Hour for Timezone: %s" % (
        ctx['_nt'].sts[station]['tzname'],))
    ax.set_xticks(range(1, 25, 4))
    ax.set_xticklabels(['Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'])
    return fig


if __name__ == '__main__':
    plotter(dict())
