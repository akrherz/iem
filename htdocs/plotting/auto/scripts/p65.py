import psycopg2.extras
import numpy as np
import datetime
import calendar
import pandas as pd
from pyiem.network import Table as NetworkTable

PDICT = {'cold': 'Coldest Temperature',
         'hot': 'Hottest Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot displays the frequency of a given day
    in the month having the coldest high or lowtemperature of that month for
    a year."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='month', name='month', default='3',
             label='Select Month:'),
        dict(type="select", name='dir', default='cold',
             label='Select variable to plot:', options=PDICT),
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
    month = int(fdict.get('month', 3))
    mydir = fdict.get('dir', 'cold')
    ts = datetime.datetime(2000, month, 1)
    ets = ts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)
    days = int((ets - ts).days)

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    s = "ASC" if mydir == 'cold' else 'DESC'
    cursor.execute("""
        with ranks as (
            select day, high, low,
    rank() OVER (PARTITION by year ORDER by high """ + s + """) as high_rank,
    rank() OVER (PARTITION by year ORDER by low """ + s + """) as low_rank
            from """ + table + """ where station = %s and month = %s),
        highs as (
            SELECT extract(day from day) as dom, count(*) from ranks
            where high_rank = 1 GROUP by dom),
        lows as (
            SELECT extract(day from day) as dom, count(*) from ranks
            where low_rank = 1 GROUP by dom)

        select coalesce(h.dom, l.dom), h.count, l.count from
        highs h FULL OUTER JOIN lows l on (h.dom = l.dom) ORDER by h.dom
    """, (station, month))
    high_hits = np.zeros((31,), 'f')
    low_hits = np.zeros((31,), 'f')
    for row in cursor:
        high_hits[int(row[0])-1] = row[1]
        low_hits[int(row[0])-1] = row[2]

    df = pd.DataFrame(dict(day=np.arange(1, days + 1),
                           high=high_hits[:days],
                           low=low_hits[:days]))

    fig, ax = plt.subplots(2, 1, sharex=True)
    lbl = 'Coldest' if mydir == 'cold' else 'Hottest'
    ax[0].set_title(("[%s] %s\nFrequency of Day in %s\n"
                     "Having %s High Temperature of %s"
                     ) % (station, nt.sts[station]['name'],
                          calendar.month_name[month], lbl,
                          calendar.month_name[month]), fontsize=10)
    ax[0].set_ylabel("Years (ties split)")

    ax[0].grid(True)
    ax[0].bar(np.arange(1, 32) - 0.4, high_hits)

    ax[1].set_title(("Having %s Low Temperature of %s"
                     ) % (lbl, calendar.month_name[month], ),
                    fontsize=10)
    ax[1].set_ylabel("Years (ties split)")
    ax[1].grid(True)
    ax[1].set_xlabel("Day of %s" % (calendar.month_name[month], ))
    ax[1].bar(np.arange(1, 32) - 0.4, low_hits)
    ax[1].set_xlim(0.5, days + 0.5)

    return fig, df
