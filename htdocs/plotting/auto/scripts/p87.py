import psycopg2.extras
from pyiem.network import Table as NetworkTable
import numpy as np
import pandas as pd
import datetime
from pyiem.util import get_autoplot_context

PDICT = {'TS': 'Thunder (TS)',
         '-SN': 'Light Snow (-SN)',
         'PSN': 'Heavy Snow (+SN)',  # +SN causes CGI issues
         'FZFG': 'Freezing Fog (FZFG)',
         'FG': 'Fog (FG)',
         'BLSN': 'Blowing Snow (BLSN)'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """Frequency plot partitioned by hour and week of the
    year for a given METAR code to appear in the present weather. If your
    favorite METAR code is not available in the listing, please let us know!
    If multiple reports occurred within the same hour during one week, it would
    only count as one in this analysis."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='select', name='code', default='TS', options=PDICT,
             label='Code appearing in present weather:'),
        dict(type='year', name='syear', default=1971,
             label='Start Year of Analysis (inclusive):'),
        dict(type='year', name='eyear', default=datetime.date.today().year,
             label='End Year of Analysis (inclusive):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['zstation']
    network = ctx['network']
    syear = ctx['syear']
    eyear = ctx['eyear']
    sts = datetime.date(syear, 1, 1)
    ets = datetime.date(eyear + 1, 1, 1)
    nt = NetworkTable(network)
    code = ctx['code']
    if code == 'PSN':
        code = "+SN"
        PDICT['+SN'] = PDICT['PSN']

    data = np.ma.zeros((24, 52), 'f')

    cursor.execute("""
    WITH data as (
    SELECT valid at time zone %s + '10 minutes'::interval as v
    from alldata where
    station = %s and presentwx LIKE '%%""" + code + """%%'
    and valid > %s and valid < %s)

    SELECT distinct extract(week from v) as week,
    extract(year from v) as year, extract(hour from v) as hour
    from data
    """, (nt.sts[station]['tzname'], station, sts, ets))

    minyear = 2099
    maxyear = 1800
    for row in cursor:
        if row[0] > 52:
            continue
        data[row[2], row[0]-1] += 1
        minyear = min([minyear, row[1]])
        maxyear = max([maxyear, row[1]])
    if cursor.rowcount == 0:
        raise Exception("No Data Found!")
    rows = []
    for week in range(52):
        for hour in range(24):
            rows.append(dict(hour=hour, week=(week+1), count=data[hour, week]))
    df = pd.DataFrame(rows)
    data.mask = np.where(data == 0, True, False)
    fig = plt.Figure()
    ax = plt.axes([0.1, 0.25, 0.7, 0.65])
    cax = plt.axes([0.82, 0.02, 0.02, 0.17])

    res = ax.imshow(data, aspect='auto', rasterized=True,
                    interpolation='nearest')
    fig.colorbar(res, cax=cax)
    xloc = plt.MaxNLocator(4)
    cax.yaxis.set_major_locator(xloc)
    cax.set_ylabel("Count")
    ax.set_ylim(-0.5, 23.5)
    ax.set_yticks((0, 4, 8, 12, 16, 20))
    ax.set_ylabel("Local Time, %s" % (nt.sts[station]['tzname'],))
    ax.set_yticklabels(('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
    ax.set_title(("[%s] %s %s Reports\n[%.0f - %.0f]"
                  " by hour and by week of the year"
                  ) % (station, nt.sts[station]['name'],
                       PDICT[code], minyear, maxyear))
    ax.grid(True)
    ax.set_xticks(np.arange(0, 55, 7))
    plt.setp(ax.get_xticklabels(), visible=False)

    # Bottom grid
    lax = plt.axes([0.1, 0.1, 0.7, 0.15])
    lax.bar(np.arange(0, 52), np.ma.sum(data, 0), facecolor='tan')
    lax.set_xlim(-0.5, 51.5)
    lax.grid(True)
    yloc = plt.MaxNLocator(3)
    lax.yaxis.set_major_locator(yloc)
    lax.set_xticks(np.arange(0, 55, 7))
    lax.set_xticklabels(('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15',
                         'Sep 2', 'Oct 21', 'Dec 9'))
    lax.yaxis.get_major_ticks()[-1].label1.set_visible(False)

    # Right grid
    rax = plt.axes([0.8, 0.25, 0.15, 0.65])
    rax.barh(np.arange(0, 24)-0.4, np.ma.sum(data, 1), facecolor='tan')
    rax.set_ylim(-0.5, 23.5)
    rax.set_yticks([])
    xloc = plt.MaxNLocator(3)
    rax.xaxis.set_major_locator(xloc)
    rax.xaxis.get_major_ticks()[0].label1.set_visible(False)
    rax.grid(True)

    return fig, df
