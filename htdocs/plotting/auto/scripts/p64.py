import psycopg2.extras
import numpy as np
import calendar
import datetime
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context

PDICT = {'first': 'First Snowfall after 1 July',
         'last': 'Last Snowfall before 1 July'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart displays either the first or last date
    of the winter season with a snowfall of a given intensity.  The snowfall
    and snow depth data is not of great quality, so please be careful with
    this plot."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:', network='IACLIMATE'),
        dict(type='text', name='threshold', default='1',
             label='First Snowfall Threshold (T for trace)'),
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
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']
    mydir = ctx['dir']
    threshold = ctx['threshold']
    threshold = 0.0001 if threshold == 'T' else float(threshold)

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    syear = max(1893, nt.sts[station]['archive_begin'].year)
    eyear = datetime.datetime.now().year

    snow = np.zeros((eyear - syear + 1, 366))
    snowd = np.ones((eyear - syear + 1, 366)) * 99
    cursor.execute("""
        SELECT extract(doy from day), year, snow, snowd from """ + table + """
        where station = %s and year >= %s
    """, (station, syear))
    for row in cursor:
        snow[row[1] - syear, int(row[0] - 1)] = row[2]
        snowd[row[1] - syear, int(row[0] - 1)] = row[3]

    rows = []
    for i, year in enumerate(range(syear, eyear)):
        s = tuple(snow[i, 183:]) + tuple(snow[i+1, :183])
        sd = tuple(snowd[i, 183:]) + tuple(snowd[i+1, :183])
        idx = np.where(np.array(s) >= threshold, 1, 0)
        if np.max(idx) == 0:
            continue
        if mydir == 'first':
            idx = tuple(idx).index(1)
        else:
            idx = 365 - tuple(idx[::-1]).index(1)
        for sfree in range(idx+1, 366):
            if sd[sfree] <= 0.01:
                break
        cnt = sfree - idx
        if cnt >= 30:
            color = 'purple'
        elif cnt >= 11:
            color = 'g'
        elif cnt >= 3:
            color = 'b'
        else:
            color = 'r'
        # print year, idx, s[idx], sd[idx:sfree]
        dt = datetime.date(year, 1, 1) + datetime.timedelta(days=(idx+183))
        rows.append(dict(year=year, snow_date=dt, snow_doy=(idx+183),
                         color=color, days=cnt,
                         snowfree_doy=(sfree+183), snowfall=s[idx]))

    df = pd.DataFrame(rows)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.scatter(df['snow_doy'], df['snowfall'], facecolor=df['color'],
               edgecolor=df['color'], s=100)
    for _, row in df.iterrows():
        ax.scatter(row['snowfree_doy'], row['snowfall'], marker='x', s=100,
                   color=row['color'])
        ax.plot([row['snow_doy'], row['snowfree_doy']],
                [row['snowfall'], row['snowfall']], lw='2', color=row['color'])
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
                   1 + 366, 32 + 366, 60 + 366, 91 + 366, 121 + 366,
                   152 + 366, 182 + 366, 213 + 366, 244 + 366, 274 + 366,
                   305 + 366, 335 + 366])
    ax.set_xticklabels(calendar.month_abbr[1:] + calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylim(bottom=0)
    ax2 = ax.twinx()
    p = np.percentile(df['snow_doy'].values, np.arange(100))
    ax2.plot(p, np.arange(100), lw=2, color='k')
    ax2.set_ylabel(("Frequency of %s Date (CDF) [%%]"
                    ) % ('Start' if mydir == 'first' else 'Last', ))
    ax.set_ylabel('Snowfall [inch], Avg: %.1f inch' % (df['snowfall'].mean(),))
    ax.set_title(('[%s] %s %s %s Snowfall\n'
                  '(color is how long snow remained)'
                  '') % (
        station, nt.sts[station]['name'],
        'Last' if mydir == 'last' else 'First',
        'Trace+' if threshold < 0.1 else "%.2f+ Inch" % (threshold,))
                 )
    p0 = plt.Rectangle((0, 0), 1, 1, fc="purple")
    p1 = plt.Rectangle((0, 0), 1, 1, fc="g")
    p2 = plt.Rectangle((0, 0), 1, 1, fc="b")
    p3 = plt.Rectangle((0, 0), 1, 1, fc="r")
    ax.legend((p0, p1, p2, p3), (
        '> 31 days [%s]' % (len(df[df['color'] == 'purple'].index), ),
        '10 - 31 [%s]' % (len(df[df['color'] == 'g'].index), ),
        '3 - 10 [%s]' % (len(df[df['color'] == 'b'].index), ),
        '< 3 days [%s]' % (len(df[df['color'] == 'r'].index), )),
              ncol=4, fontsize=11, loc=(0., -0.15))
    ax.set_xlim(df['snow_doy'].min()-5,  df['snowfree_doy'].max()+5)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width,
                     box.height * 0.9])
    ax2.set_position([box.x0, box.y0 + box.height * 0.1, box.width,
                     box.height * 0.9])
    df.set_index('year', inplace=True)
    del(df['color'])
    return fig, df


if __name__ == '__main__':
    plotter(dict(dir='last'))
