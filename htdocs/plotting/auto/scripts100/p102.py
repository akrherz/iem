import psycopg2
import datetime
import numpy as np
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable

MARKERS = ['8', '>', '<', 'v', 'o', 'h', '*']


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 3600
    d['description'] = """"""
    today = datetime.date.today()
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True),
        dict(type="year", name="year", min=2006, default=2006,
             label="Start Year"),
        dict(type="year", name="eyear", min=2006, default=today.year,
             label="End Year (inclusive)"),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    station = fdict.get('station', 'DMX')[:4]
    syear = int(fdict.get('syear', 2006))
    eyear = int(fdict.get('eyear', 2015))
    nt = NetworkTable('WFO')
    wfo_limiter = " and wfo = '%s' " % (
        station if len(station) == 3 else station[1:],)
    if station == '_ALL':
        wfo_limiter = ''

    df = read_sql("""
        select extract(year from valid) as yr, upper(source) as src,
        count(*) from lsrs
        where valid > '""" + str(syear) + """-01-01' and
        valid < '""" + str(eyear + 1) + """-01-01' """ + wfo_limiter + """
        GROUP by yr, src
    """, pgconn)
    df['rank'] = df.groupby(['yr'])['count'].rank(ascending=False,
                                                  method='first')
    (fig, ax) = plt.subplots(1, 1)
    # Do 2006 as left side
    dyear = df[df['yr'] == syear].sort(['rank'], ascending=True)
    i = 1
    ylabels = []
    for _, row in dyear.iterrows():
        src = row['src']
        ylabels.append(src)
        d = df[df['src'] == src].sort(['yr'])
        ax.plot(np.array(d['yr']), np.array(d['rank']), lw=2, label=src,
                marker=MARKERS[i % len(MARKERS)])
        i += 1
        if i > 20:
            break
    ax.set_yticks(range(1, len(ylabels)+1))
    ax.set_yticklabels(["%s %s" % (s, i+1) for i, s in enumerate(ylabels)])
    ax.set_ylim(0.5, 20.5)

    ax2 = ax.twinx()
    # Do last year as right side
    dyear = df[df['yr'] == eyear].sort(['rank'], ascending=True)
    i = 1
    y2labels = []
    for _, row in dyear.iterrows():
        src = row['src']
        y2labels.append(src)
        if src in ylabels:
            continue
        ylabels.append(src)
        d = df[df['src'] == src].sort(['yr'])
        ax.plot(np.array(d['yr']), np.array(d['rank']), lw=2, label=src,
                marker=MARKERS[i % len(MARKERS)])
        i += 1
        if i > 20:
            break

    ax2.set_yticks(range(1, len(y2labels)+1))
    ax2.set_yticklabels(["%s %s" % (i+1, s) for i, s in enumerate(y2labels)])
    ax2.set_ylim(0.5, 20.5)

    ax.set_position([0.3, 0.15, 0.4, 0.75])
    ax2.set_position([0.3, 0.15, 0.4, 0.75])
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    ax.grid()

    fig.text(0.15, 0.9, "%s" % (syear,), fontsize=14, ha='center')
    fig.text(0.85, 0.9, "%s" % (eyear,), fontsize=14, ha='center')

    fig.text(0.5, 0.95, "NWS %s Local Storm Report Sources Ranks" % (
                "ALL WFOs" if station == '_ALL' else nt.sts[station]['name'],),
             ha='center')

    return fig, df
