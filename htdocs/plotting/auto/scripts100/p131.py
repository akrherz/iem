import psycopg2
import datetime
from collections import OrderedDict
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context

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
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot displays the frequency of having overcast
    conditions reported by air temperature.  More specifically, this script
    looks for the report of 'OVC' within the METAR sky conditions.  Many
    caveats apply with the reporting changes of this over the years."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),

    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    month = ctx['month']

    nt = NetworkTable(network)

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

    df = read_sql("""
        SELECT tmpf::int as t,
        SUM(case when (skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC'
            or skyc4 = 'OVC') then 1 else 0 end) as hits,
        count(*)
        from alldata where station = %s
        and tmpf is not null and extract(month from valid) in %s
        GROUP by t ORDER by t ASC
        """, pgconn, params=(station,  tuple(months)), index_col=None)
    df['freq'] = df['hits'] / df['count'] * 100.
    df2 = df[df['count'] > 2]
    avg = df['hits'].sum() / float(df['count'].sum()) * 100.

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df2['t'], df2['freq'], ec='green', fc='green', width=1)
    ax.grid(True, zorder=11)
    ax.set_title(("%s [%s]\nFrequency of Overcast Clouds by "
                  "Air Temperature (month=%s) "
                  "(%s-%s)\n"
                  "(must have 3+ hourly observations at the given temperature)"
                  ) % (nt.sts[station]['name'], station, month.upper(),
                       nt.sts[station]['archive_begin'].year,
                       datetime.datetime.now().year), size=10)

    ax.set_ylabel("Cloudiness Frequency [%]")
    ax.set_ylim(0, 100)
    ax.set_xlabel("Air Temperature $^\circ$F")
    if df2['t'].min() < 30:
        ax.axvline(32, lw=2, color='k')
        ax.text(32, -4, "32", ha='center')
    ax.axhline(avg, lw=2, color='k')
    ax.text(df2['t'].min() + 5, avg + 2, "Avg: %.1f%%" % (avg,))

    return fig, df
