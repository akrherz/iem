import psycopg2.extras
import numpy as np
import datetime
import calendar
from pyiem.network import Table as NetworkTable

PDICT = {'above': 'At or Above Threshold',
         'below': 'Below Threshold'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """This plot presents the hourly frequency of having
    a certain temperature above or below a given threshold.  Values are
    partitioned by week of the year to smooth out some of the day to day
    variation."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='text', name='threshold', default=32,
             label='Temperature Threshold (F)'),
        dict(type='select', name='direction', default='below',
             label='Threshold direction:', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mpcolors
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    threshold = int(fdict.get('threshold', 32))
    direction = fdict.get('direction', 'below')

    nt = NetworkTable(network)

    mydir = "<" if direction == 'below' else '>='

    cursor.execute("""
    WITH data as (
 SELECT extract(week from valid) as week,
 extract(hour from (valid + '10 minutes'::interval) at time zone %s) as hour,
 tmpf from alldata where station = %s and tmpf between -70 and 140
    )
    SELECT week, hour, sum(case when tmpf """+mydir+""" %s then 1 else 0 end),
    count(*) from data GROUP by week, hour
    """, (nt.sts[station]['tzname'], station, threshold))
    data = np.zeros((24, 53), 'f')
    for row in cursor:
        data[row[1], row[0]-1] = row[2] / float(row[3]) * 100.

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(float(ts.strftime("%j")) / 7.0)

    (fig, ax) = plt.subplots(1, 1)
    cmap = plt.get_cmap('jet')
    cmap.set_under('white')
    bins = np.arange(0, 101, 5)
    bins[0] = 1
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    res = ax.imshow(data, interpolation='nearest', aspect='auto',
                    extent=[0, 53, 24, 0], cmap=cmap, norm=norm)
    fig.colorbar(res, label='%', extend='min')
    ax.grid(True, zorder=11)
    ax.set_title("%s [%s]\nHourly Temp Frequencies %s %s$^\circ$F (%s-%s)" % (
                nt.sts[station]['name'], station, PDICT[direction], threshold,
                nt.sts[station]['archive_begin'].year,
                datetime.datetime.now().year), size=12)

    ax.set_xticks(xticks)
    ax.set_ylabel("%s Timezone" % (nt.sts[station]['tzname'],))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    ax.set_ylim(0, 24)
    ax.set_yticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_yticklabels(['12 AM', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM',
                        'Mid'])

    return fig
