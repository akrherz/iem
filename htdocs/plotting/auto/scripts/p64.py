import psycopg2.extras
import numpy as np
import datetime
import pandas as pd
from pyiem.network import Table as NetworkTable

PDICT = {'first': 'First Snowfall between Jul - Dec',
         'last': 'Last Snowfall between Jan - Jun'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart plots the last one plus inch snowfall
    of each winter season and then the number of days the snow persisted as
    per snowdepth measurements."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type="select", name='dir', default='last', options=PDICT,
             label='Which Variable to Plot?'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA2203')
    mydir = fdict.get('dir', 'last')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    syear = max(1893, nt.sts[station]['archive_begin'].year)
    eyear = datetime.datetime.now().year

    doy = []
    snow = []
    days = []
    cnts = []
    years = []
    for year in range(syear, eyear):
        sts = datetime.date(year, 1 if mydir == 'last' else 7, 1)
        ets = datetime.date(year, 7 if mydir == 'last' else 12,
                            1 if mydir == 'last' else 31)
        cursor.execute("""
        SELECT extract(doy from day), day, snow, snowd from """ + table + """
        where station = %s and day BETWEEN
        %s and %s ORDER by day ASC
        """, (station, sts, ets))
        found = False
        thissnow = 0
        d = None
        for row in cursor:
            if found and mydir == 'first' and row[3] < 0.1:
                break
            if row[2] >= 1:
                found = True
                d = row[0]
                thissnow = row[2]
                cnt = 0
            if row[3] > 0 and found:
                cnt += 1
        if d is None:
            continue
        cnts.append(cnt)
        years.append(year)
        doy.append(d)
        snow.append(thissnow)
        if cnt >= 11:
            days.append('g')
        elif cnt >= 3:
            days.append('b')
        else:
            days.append('r')

    doy = np.array(doy)
    p = np.percentile(doy, np.arange(100))
    df = pd.DataFrame(dict(doy=doy, snow=snow, year=years))

    (fig, ax) = plt.subplots(1, 1)

    ax.scatter(doy, snow, facecolor=days, edgecolor=days, s=100)
    for x, y, l, c in zip(doy, snow, cnts, days):
        ax.scatter(x+l, y, marker='x', s=100, color=c)
        ax.plot([x, x+l], [y, y], lw='2', color=c)
    if mydir == 'last':
        ax.set_xticks((1, 32, 60, 91, 121, 152))
        ax.set_xticklabels(('Jan 1', 'Feb 1', 'Mar 1', 'Apr 1', 'May 1',
                            'Jun 1'))
    else:
        ax.set_xticks((244, 274, 305, 335))
        ax.set_xticklabels(('Sep 1', 'Oct 1', 'Nov 1', 'Dec 1'))
    ax.grid(True)
    ax.set_ylim(bottom=0)
    ax2 = ax.twinx()
    ax2.plot(p, np.arange(100), lw=2, color='k')
    ax2.set_ylabel(("Frequency of %s Date (CDF) [%%]"
                    ) % ('Start' if mydir == 'first' else 'Last', ))
    ax.set_ylabel('Snowfall [inch]')
    ax.set_title(('[%s] %s %s 1+ Inch Snowfall\n'
                  '(color is how long snow remained)'
                  '') % (station, nt.sts[station]['name'],
                         'Last' if mydir == 'last' else 'First'))
    p1 = plt.Rectangle((0, 0), 1, 1, fc="g")
    p2 = plt.Rectangle((0, 0), 1, 1, fc="b")
    p3 = plt.Rectangle((0, 0), 1, 1, fc="r")
    ax.legend((p1, p2, p3), ('> 10 days', '3 - 10', '< 3 days'),
              ncol=3, fontsize=11, loc=(0., -0.15))
    ax.set_xlim(min(doy)-5,  max(doy)+5)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width,
                     box.height * 0.9])
    ax2.set_position([box.x0, box.y0 + box.height * 0.1, box.width,
                     box.height * 0.9])

    return fig, df
