"""first and last snowfalls"""
import calendar
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.reference import TRACE_VALUE

PDICT = {'first': 'First Snowfall after 1 July',
         'last': 'Last Snowfall before 1 July'}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart displays either the first or last date
    of the winter season with a snowfall of a given intensity.  The snowfall
    and snow depth data is not of great quality, so please be careful with
    this plot."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='text', name='threshold', default='1',
             label='First Snowfall Threshold (T for trace)'),
        dict(type="select", name='dir', default='last', options=PDICT,
             label='Which Variable to Plot?'),
    ]
    return desc


def get_data(ctx):
    """Get some data please"""
    pgconn = get_dbconn('coop', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    station = ctx['station']
    threshold = ctx['threshold']
    threshold = TRACE_VALUE if threshold == 'T' else float(threshold)

    table = "alldata_%s" % (station[:2],)
    ctx['nt'] = NetworkTable("%sCLIMATE" % (station[:2],))
    syear = max(1893, ctx['nt'].sts[station]['archive_begin'].year)
    eyear = datetime.datetime.now().year

    snow = np.zeros((eyear - syear + 1, 366))
    snowd = np.zeros((eyear - syear + 1, 366))
    cursor.execute("""
        SELECT extract(doy from day), year, snow, snowd from """ + table + """
        where station = %s and year >= %s
    """, (station, syear))
    for row in cursor:
        # On non-leap year, duplicate our snowdepth on 31 Dec
        if row[0] == 365 and not calendar.isleap(row[1]):
            snowd[row[1] - syear, int(row[0])] = row[3]
        snow[row[1] - syear, int(row[0] - 1)] = row[2]
        snowd[row[1] - syear, int(row[0] - 1)] = row[3]
    # reset any nan
    snow = np.where(np.isnan(snow), 0, snow)
    snowd = np.where(np.isnan(snowd), 0, snowd)

    rows = []
    for i, year in enumerate(range(syear, eyear)):
        # Slap the years together so we cross over 1 Jan
        snowfall = tuple(snow[i, 183:]) + tuple(snow[i+1, :183])
        snowdepth = tuple(snowd[i, 183:]) + tuple(snowd[i+1, :183])
        hits = np.where(np.array(snowfall) >= threshold)[0]
        if hits.size == 0:
            continue
        idx = hits[0] if ctx['dir'] == 'first' else hits[-1]
        # Compute how long this stuck around
        sfree = idx + 1
        for sfree in range(idx+1, 366):
            if snowdepth[sfree] <= 0.01:
                break
        days = sfree - idx
        if days >= 30:
            color = 'purple'
        elif days >= 11:
            color = 'g'
        elif days >= 3:
            color = 'b'
        else:
            color = 'r'
        # print("year: %s idx: %s days: %s %s" % (year, idx, days, snowdepth))
        dt = (
            datetime.date(year, 1, 1) +
            datetime.timedelta(days=(int(idx)+183))
        )
        rows.append(dict(year=year, snow_date=dt, snow_doy=(idx+183),
                         color=color, days=days,
                         snowfree_doy=(sfree+183),
                         snowfall=snowfall[idx]))

    return pd.DataFrame(rows)


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    df = get_data(ctx)

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
    ptile = np.percentile(df['snow_doy'].values, np.arange(100))
    ax2.plot(ptile, np.arange(100), lw=2, color='k')
    ax2.set_ylabel(("Frequency of %s Date (CDF) [%%] (black line)"
                    ) % ('Start' if ctx['dir'] == 'first' else 'Last', ))
    ax.set_ylabel('Snowfall [inch], Avg: %.1f inch' % (df['snowfall'].mean(),))
    ax.set_title(
        ('[%s] %s %s %s Snowfall\n(color is how long snow remained)'
         ) % (ctx['station'], ctx['nt'].sts[ctx['station']]['name'],
              'Last' if ctx['dir'] == 'last' else 'First',
              ('Trace+' if ctx['threshold'] == 'T'
               else "%.2f+ Inch" % (ctx['threshold'],))))
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
    ax.set_xlim(df['snow_doy'].min() - 5, df['snowfree_doy'].max() + 5)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width,
                     box.height * 0.9])
    ax2.set_position([box.x0, box.y0 + box.height * 0.1, box.width,
                     box.height * 0.9])
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax2.set_ylim(0, 101)
    df.set_index('year', inplace=True)
    del df['color']
    return fig, df


if __name__ == '__main__':
    plotter(
        dict(threshold='T', dir='first', station='IATDSM', network='IACLIMATE')
    )
