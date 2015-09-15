import matplotlib.patheffects as PathEffects
import psycopg2.extras
import datetime
import calendar
from pyiem.network import Table as NetworkTable
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['cache'] = 86400
    d['description'] = """This plot displays the frequency of having a
    reported wind speed be above a given threshold by reported temperature
    and by month."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='text', name='threshold', default=10,
             label='Wind Speed Threshold (knots)'),
        dict(type='month', name='month', default='3',
             label='Select Month:'),
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
    threshold = int(fdict.get('threshold', 10))
    month = int(fdict.get('month', 3))

    nt = NetworkTable(network)

    cursor.execute("""
    WITH data as (
    SELECT tmpf::int as t, sknt from alldata where station = %s
    and extract(month from valid) = %s and tmpf is not null
    and sknt >= 0)

    SELECT t, sum(case when sknt >= %s then 1 else 0 end), count(*) from data
    GROUP by t ORDER by t ASC
    """, (station, month, threshold))
    tmpf = []
    events = []
    total = []
    hits = 0
    cnt = 0
    for row in cursor:
        if row[2] < 3:
            continue
        tmpf.append(row[0])
        hits += row[1]
        cnt += row[2]
        events.append(row[1])
        total.append(row[2])

    df = pd.DataFrame(dict(tmpf=pd.Series(tmpf), events=pd.Series(events),
                           total=pd.Series(total)))

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(tmpf, df['events'] / df['total'] * 100., width=1.1, ec='green',
           fc='green')
    avgval = hits / float(cnt) * 100.
    ax.axhline(avgval, lw=2, zorder=2)
    txt = ax.text(tmpf[10], avgval + 1, "Average: %.1f%%" % (avgval,),
                  va='bottom', zorder=2, color='yellow', fontsize=14)
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="k")])
    ax.grid(True, zorder=11)
    ax.set_title(("%s [%s]\nFrequency of %s+ knot Wind Speeds by Temperature "
                  "for %s (%s-%s)\n"
                  "(must have 3+ hourly observations at the given temperature)"
                  ) % (nt.sts[station]['name'], station, threshold,
                       calendar.month_name[month],
                       nt.sts[station]['archive_begin'].year,
                       datetime.datetime.now().year), size=10)

    ax.set_ylabel("Frequency [%]")
    ax.set_ylim(0, 100)
    ax.set_xlim(min(tmpf)-3, max(tmpf)+3)
    ax.set_xlabel("Air Temperature $^\circ$F")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])

    return fig, df
