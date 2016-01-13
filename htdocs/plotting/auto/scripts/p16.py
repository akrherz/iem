import psycopg2
from pyiem.network import Table as NetworkTable
import datetime
from pandas.io.sql import read_sql
from collections import OrderedDict

PDICT = OrderedDict([
         ('ts', 'Thunderstorm (TS) Reported'),
         ('tmpf_above', 'Temperature At or Above Threshold (F)'),
         ('tmpf_below', 'Temperature Below Threshold (F)'),
         ('dwpf_above', 'Dew Point At or Above Threshold (F)'),
         ('dwpf_below', 'Dew Point Below Threshold (F)')])

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
    d['description'] = """This application generates a wind rose for a given
    criterion being meet. A wind rose plot is a convenient way of summarizing
    wind speed and direction."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='select', name='opt', default='ts',
             label='Which metric to plot?', options=PDICT),
        dict(type='select', name='month', default='all',
             label='Month Limiter', options=MDICT),
        dict(type='text', name='threshold', default='80',
             label='Threshold (when appropriate):')
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from windrose import WindroseAxes
    from matplotlib.patches import Rectangle
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    threshold = int(fdict.get('threshold', 80))
    opt = fdict.get('opt', 'ts')
    month = fdict.get('month', 'all')
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

    limiter = "presentwx ~* 'TS'"
    title = "Thunderstorm (TS) contained in METAR"
    if opt == 'tmpf_above':
        limiter = "round(tmpf::numeric,0) >= %s" % (threshold,)
        title = "Air Temp at or above %s$^\circ$F" % (threshold,)
    elif opt == 'tmpf_below':
        limiter = "round(tmpf::numeric,0) < %s" % (threshold,)
        title = "Air Temp below %s$^\circ$F" % (threshold,)
    elif opt == 'dwpf_below':
        limiter = "round(dwpf::numeric,0) < %s" % (threshold,)
        title = "Dew Point below %s$^\circ$F" % (threshold,)
    elif opt == 'dwpf_above':
        limiter = "round(tmpf::numeric,0) >= %s" % (threshold,)
        title = "Dew Point at or above %s$^\circ$F" % (threshold,)

    df = read_sql("""
     SELECT valid, drct, sknt * 1.15 as smph from alldata
     where station = %s and
     """+limiter+""" and sknt > 0 and drct >= 0 and drct <= 360
     and extract(month from valid) in %s
    """, pgconn, params=(station, tuple(months)), index_col='valid')
    minvalid = df.index.min()
    maxvalid = df.index.max()

    fig = plt.figure(figsize=(6, 7.2), facecolor='w', edgecolor='w')
    rect = [0.08, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    ax.bar(df['drct'].values, df['smph'].values,
           normed=True, bins=[0, 2, 5, 7, 10, 15, 20], opening=0.8,
           edgecolor='white', nsector=18)
    handles = []
    for p in ax.patches_list:
        color = p.get_facecolor()
        handles.append(Rectangle((0, 0), 0.1, 0.3,
                                 facecolor=color, edgecolor='black'))
    l = fig.legend(handles,
                   ('2-5', '5-7', '7-10', '10-15', '15-20', '20+'),
                   loc=(0.01, 0.03), ncol=6,
                   title='Wind Speed [%s]' % ('mph',),
                   mode=None, columnspacing=0.9, handletextpad=0.45)
    plt.setp(l.get_texts(), fontsize=10)

    plt.gcf().text(0.5, 0.99,
                   ("%s-%s %s Wind Rose, month=%s\n%s\nWhen  "
                    "%s") % (minvalid.year,
                             maxvalid.year, station, month.upper(),
                             nt.sts[station]['name'],
                             title),
                   fontsize=16, ha='center', va='top')
    plt.gcf().text(0.95, 0.12, "n=%s" % (len(df.index),),
                   verticalalignment="bottom", ha='right')

    return fig, df

if __name__ == '__main__':
    plotter(dict())
