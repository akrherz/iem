
import psycopg2.extras
import pytz
from pyiem.network import Table as NetworkTable
import datetime
import calendar
import numpy as np
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot presents the frequency of a given hourly
    temperature being within the bounds of two temperature thresholds.
    """
    d['data'] = True
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='zhour', name='hour', default=20,
             label='At Time (UTC):'),
        dict(type='text', name='t1', default=70,
             label='Lower Temperature Bound (inclusive):'),
        dict(type='text', name='t2', default=79,
             label='Upper Temperature Bound (inclusive):'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    hour = int(fdict.get('hour', 20))
    t1 = int(fdict.get('t1', 70))
    t2 = int(fdict.get('t2', 70))
    nt = NetworkTable(network)

    cursor.execute("""
    WITH obs as (
        SELECT date_trunc('hour', valid) as t, avg(tmpf) as tmp from alldata
        WHERE station = %s and (extract(minute from valid) > 50 or
        extract(minute from valid) = 10) and
        extract(hour from valid at time zone 'UTC') = %s and tmpf is not null
        GROUP by t
    )
    SELECT extract(month from t) as mo,
    sum(case when round(tmp::numeric,0) >= %s
        and round(tmp::numeric,0) <= %s then 1 else 0 end),
    count(*) from obs GROUP by mo ORDER by mo ASC
    """, (station, hour, t1, t2))
    months = []
    freq = []
    rows = []
    for row in cursor:
        val = float(row[1]) / float(row[2]) * 100.
        rows.append(dict(month=row[0], val=val))
        months.append(row[0])
        freq.append(val)
    df = pd.DataFrame(rows)
    (fig, ax) = plt.subplots(1, 1)
    bars = ax.bar(np.arange(1, 13) - 0.4, freq, fc='blue')
    for i, bar in enumerate(bars):
        ax.text(i+1, bar.get_height()+3, "%.1f%%" % (bar.get_height(),),
                ha='center', fontsize=12)
    ax.set_xticks(range(0, 13))
    ax.set_xticklabels(calendar.month_abbr)
    ax.grid(True)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Frequency [%]")
    ut = datetime.datetime(2000, 1, 1, hour, 0)
    ut = ut.replace(tzinfo=pytz.timezone("UTC"))
    localt = ut.astimezone(pytz.timezone(nt.sts[station]['tzname']))
    ax.set_xlim(0.5, 12.5)
    ax.set_title(("%s [%s]\nFrequency of %s UTC (%s LST) "
                  "Temp between %s$^\circ$F and %s$^\circ$F"
                  ) % (nt.sts[station]['name'], station, hour,
                       localt.strftime("%-I %p"), t1, t2))

    return fig, df
