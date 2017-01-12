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

METRICS = OrderedDict([
    ('dwpf', 'Dew Point Temp (F)'),
    ('tmpf', 'Air Temp (F)'),
    ])

DIRS = OrderedDict([
    ('aoa', 'At or Above'),
    ('below', 'Below'),
    ])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """Based on available hourly observation reports
    by METAR stations, this application presents the frequency of number
    of hours for a given month or season at a given threshold.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             network='IA_ASOS', label='Select Station:'),
        dict(type='select', name='var', default='dwpf',
             label='Which Variable', options=METRICS),
        dict(type='select', name='dir', default='aoa',
             label='Threshold Direction:', options=DIRS),
        dict(type="int", name='thres', default=65,
             label='Threshold'),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='year', min=1973, default=datetime.date.today().year,
             label='Year to Highlight', name='year'),

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
    varname = ctx['var']
    mydir = ctx['dir']
    threshold = ctx['thres']
    year = ctx['year']

    nt = NetworkTable(network)

    offset = 'ts'
    if month == 'all':
        months = range(1, 13)
    elif month == 'fall':
        months = [9, 10, 11]
    elif month == 'winter':
        months = [12, 1, 2]
        offset = "ts + '1 month'::interval"
    elif month == 'spring':
        months = [3, 4, 5]
    elif month == 'summer':
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-"+month+"-01", '%Y-%b-%d')
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    opp = ">=" if mydir == 'aoa' else '<'
    df = read_sql("""WITH hourly as (
        SELECT date_trunc('hour', valid + '10 minutes'::interval)
        at time zone %s as ts,
        avg(""" + varname + """)::int as d from alldata where station = %s and
        valid > '1973-01-01' and
        """ + varname + """ """ + opp + """ %s GROUP by ts)

        SELECT extract(year from """ + offset + """) as year,
        extract(hour from ts) as hour, count(*) from hourly
        WHERE extract(month from ts) in %s GROUP by year, hour
        """, pgconn, params=(nt.sts[station]['tzname'],
                             station, threshold,
                             tuple(months)),
                  index_col=None)
    if len(df.index) == 0:
        return 'Error, no results returned!'

    (fig, ax) = plt.subplots(2, 1)
    ydf = df.groupby('year').sum()
    ax[0].set_title(("(%s) %s Hours %s %s\n"
                     "%s [%s]"
                     ) % (MDICT[month], METRICS[varname], DIRS[mydir],
                          threshold, nt.sts[station]['name'], station))
    ax[0].bar(ydf.index.values, ydf['count'], align='center', fc='green',
              ec='green')
    if year in ydf.index.values:
        val = ydf.loc[year]
        ax[0].bar(year, val['count'], align='center', fc='orange',
                  ec='orange', zorder=5)
    ax[0].grid(True)
    ax[0].set_ylabel("Hours")
    ax[0].set_xlim(ydf.index.min() - 1, ydf.index.max() + 1)

    years = ydf.index.max() - ydf.index.min() + 1
    hdf = df.groupby('hour').sum() / years
    ax[1].bar(hdf.index.values, hdf['count'], align='center', fc='b',
              ec='b', label='Avg')
    thisyear = df[df['year'] == year]
    if len(thisyear.index) > 0:
        ax[1].bar(thisyear['hour'].values, thisyear['count'], align='center',
                  width=0.25, zorder=5, fc='orange', ec='orange',
                  label='%s' % (year,))
    ax[1].set_xlim(-0.5, 23.5)
    ax[1].grid(True)
    ax[1].legend(loc=(0.7, -0.22), ncol=2, fontsize=10)
    ax[1].set_ylabel("Days Per Period")
    ax[1].set_xticks(range(0, 24, 4))
    ax[1].set_xticklabels(['Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'])
    ax[1].set_xlabel("Hour of Day (%s)" % (nt.sts[station]['tzname'],),
                     ha='right')
    return fig, df

if __name__ == '__main__':
    plotter(dict(network='IA_ASOS', station='AMW'))
