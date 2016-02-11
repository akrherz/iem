import psycopg2.extras
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable
import pandas as pd

PDICT = {'touches': 'Daily Range Touches Emphasis',
         'above': 'Daily Range At or Above Emphasis'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    today = datetime.datetime.now()
    d['data'] = True
    d['description'] = """This plot presents the daily range of dew points
    as calculated by the IEM based on available observations."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='text', name='year',
             default=today.year, label='Enter Year:'),
        dict(type='text', name='emphasis', default='-99',
             label='Temperature(&deg;F) Line of Emphasis (-99 disables):'),
        dict(type='select', name='opt', label='Option for Highlighting',
             default='touches', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    nt = NetworkTable(network)
    year = int(fdict.get('year', 2014))
    emphasis = int(fdict.get('emphasis', -99))
    opt = fdict.get('opt', 'touches')

    table = "summary_%s" % (year,)

    cursor.execute("""
     select day,
     (case when max_dwpf > -90 and max_dwpf < 120
             then max_dwpf else null end) as "max-dwpf",
     (case when min_dwpf > -90 and min_dwpf < 120
             then min_dwpf else null end) as "min-dwpf"
     from """+table+""" where iemid = (select iemid from stations where
     id = %s and network = %s) ORDER by day ASC
    """, (station, network))
    rows = []
    for row in cursor:
        if row['max-dwpf'] is None or row['min-dwpf'] is None:
            continue
        rows.append(dict(day=row['day'], min_dwpf=row['min-dwpf'],
                         max_dwpf=row['max-dwpf']))
    if len(rows) == 0:
        return 'No Data Found!'
    df = pd.DataFrame(rows)
    days = np.array(df['day'])

    (fig, ax) = plt.subplots(1, 1)
    bars = ax.bar(df['day'].values,
                  (df['max_dwpf'] - df['min_dwpf']).values, ec='g', fc='g',
                  bottom=df['min_dwpf'].values, zorder=1)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
    hits = []
    if emphasis > -99:
        for i, bar in enumerate(bars):
            y = bar.get_y() + bar.get_height()
            if ((y >= emphasis and opt == 'touches') or
                    (bar.get_y() >= emphasis and opt == 'above')):
                bar.set_facecolor('r')
                bar.set_edgecolor('r')
                hits.append(df.loc[i, 'day'])
        ax.axhline(emphasis, lw=2, color='k')
        ax.text(days[-1] + datetime.timedelta(days=2),
                emphasis, "%s" % (emphasis,), ha='left',
                va='center')
    ax.grid(True)
    ax.set_ylabel("Dew Point Temperature $^\circ$F")
    ax.set_title("%s [%s] %s Daily Min/Max Dew Point\nPeriod: %s to %s" % (
                nt.sts[station]['name'], station, year,
                min(days).strftime("%-d %b"), max(days).strftime("%-d %b")))

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.05,
                     box.width, box.height * 0.95])
    ax.set_xlabel(("Days meeting emphasis: %s, first: %s last: %s"
                   ) % (len(hits),
                        hits[0].strftime("%B %d") if len(hits) > 0 else 'None',
                        hits[-1].strftime("%B %d") if len(hits) > 0 else 'None'
                        ))

    return fig, df
