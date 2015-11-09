import psycopg2
import pyiem.nws.vtec as vtec
import datetime
import numpy as np
import pandas as pd
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 3600
    d['description'] = """This chart displays the relative frequency of
    VTEC products.  This is computed by taking the unique combination of
    events and UGC county/zones.  Restating and for example, a single
    Severe Thunderstorm Warning covering portions of two counties would
    count as two events in this summary. The values plotted are relative to the
    most frequent product."""
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True),
        dict(type="year", name="syear", default=2009,
             label='Start Year (inclusive):', min=2009),
        dict(type="year", name="eyear", default=datetime.date.today().year,
             label='End Year (inclusive):', min=2009),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    pcursor = pgconn.cursor()
    syear = int(fdict.get('syear', 2009))
    eyear = int(fdict.get('eyear', 2015)) + 1
    station = fdict.get('station', 'DMX')[:4]
    sts = datetime.date(syear, 1, 1)
    ets = datetime.date(eyear, 1, 1)
    nt = NetworkTable('WFO')
    wfo_limiter = " and wfo = '%s' " % (
        station if len(station) == 3 else station[1:],)
    if station == '_ALL':
        wfo_limiter = ''

    pcursor.execute("""
        select phenomena, significance, min(issue), count(*) from warnings
        where ugc is not null and issue > %s
        and issue < %s """ + wfo_limiter + """
        GROUP by phenomena, significance ORDER by count DESC
    """, (sts, ets))
    labels = []
    vals = []
    cnt = 1
    rows = []
    for row in pcursor:
        l = "%s. %s %s (%s.%s)" % (
            cnt, vtec._phenDict.get(row[0], row[0]),
            vtec._sigDict[row[1]], row[0], row[1])
        if cnt < 26:
            labels.append(l)
            vals.append(row[3])
        rows.append(dict(phenomena=row[0],
                         significance=row[1],
                         count=row[3],
                         wfo=station))
        cnt += 1
    df = pd.DataFrame(rows)
    (fig, ax) = plt.subplots(1, 1, figsize=(7, 10))
    vals = np.array(vals)

    ax.barh(np.arange(len(vals))-0.4, vals / float(vals[0]) * 100.0)
    for i in range(1, len(vals)):
        y = vals[i] / float(vals[0]) * 100.0
        ax.text(y + 1, i, '%.1f%%' % (y,), va='center')
    fig.text(0.5, 0.95, "%s-%s NWS %s Watch/Warning/Advisory Totals" % (
                syear, eyear-1 if (eyear - 1 != syear) else '',
                "ALL WFOs" if station == '_ALL' else nt.sts[station]['name']),
             ha='center')
    fig.text(0.5, 0.05, "Event+County/Zone Count, Relative to #%s" % (
        labels[0],), ha='center', fontsize=10)
    ax.set_ylim(len(vals), -0.5)
    ax.grid(True)
    ax.set_yticklabels(labels)
    ax.set_yticks(np.arange(len(vals)))
    ax.set_position([0.5, 0.1, 0.45, 0.83])
    ax.set_xticks([0, 10, 25, 50, 75, 90, 100])

    return fig, df
