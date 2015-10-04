import psycopg2.extras
from pyiem.network import Table as NetworkTable
import datetime
import calendar
import numpy as np
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    ts = datetime.date.today()
    d['data'] = True
    d['description'] = """This chart displays the number of hourly
    observations each month that reported measurable precipitation.  Sites
    are able to report trace amounts, but those reports are not considered
    in hopes of making the long term climatology comparable.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='year', name='year', default=ts.year,
             label='Select Year:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as PathEffects
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    nt = NetworkTable(network)
    year = int(fdict.get('year', datetime.date.today().year))

    cursor.execute("""
    WITH obs as (
        SELECT distinct date_trunc('hour', valid) as t from alldata
        WHERE station = %s and p01i >= 0.01
    ), agg1 as (
        SELECT extract(year from t) as year, extract(month from t) as month,
        count(*) from obs GROUP by year, month
    ), averages as (
        SELECT month, avg(count) from agg1 GROUP by month
    ), myyear as (
        SELECT month, count from agg1 where year = %s
    )
    SELECT a.month, m.count, a.avg from averages a LEFT JOIN myyear m
    on (m.month = a.month) ORDER by a.month ASC
    """, (station, year))
    months = []
    thisyear = []
    averages = []
    for row in cursor:
        months.append(row[0])
        if row[1] is not None:
            thisyear.append(row[1])
        averages.append(row[2])
    df = pd.DataFrame(dict(month=pd.Series(months),
                           thisyear=pd.Series(thisyear),
                           average=pd.Series(averages)))
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(np.arange(1, 13)-0.4, averages, fc='blue', label='Climatology')
    bars = ax.bar(np.arange(1, len(thisyear)+1)-0.2, thisyear, width=0.4,
                  fc='yellow', label='%s' % (year,), zorder=2)
    for i, _ in enumerate(bars):
        txt = ax.text(i+1, thisyear[i]+2, "%.0f" % (thisyear[i],), ha='center')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="yellow")])

    ax.set_xticks(range(0, 13))
    ax.set_xticklabels(calendar.month_abbr)
    ax.set_xlim(0.5, 12.5)
    ax.set_yticks(np.arange(0, max(max(averages), max(thisyear)) + 20, 12))
    ax.set_ylabel("Hours with 0.01+ inch precip")
    ax.grid(True)
    ax.legend()
    ax.set_title(("%s [%s]\n"
                  "Number of Hours with *Measurable* Precipitation Reported"
                  ) % (nt.sts[station]['name'], station))

    return fig, df
