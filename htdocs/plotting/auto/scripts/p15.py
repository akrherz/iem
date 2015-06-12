import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import psycopg2.extras
import numpy as np
import calendar
import sys
import pandas as pd
from pyiem.network import Table as NetworkTable

PDICT = {'high': 'High temperature',
         'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='select', name='varname', default='high',
             label='Which metric to plot?', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    varname = fdict.get('varname', 'low')
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)

    table = "alldata_%s" % (station[:2],)

    cursor.execute("""
    with obs as
    (select month, high, lag(high) OVER (ORDER by day ASC) as lhigh,
    low, lag(low) OVER (ORDER by day ASC) as llow from """ + table + """
    where station = %s)

    SELECT month,
    sum(case when high > lhigh then 1 else 0 end) as high_greater,
    sum(case when high = lhigh then 1 else 0 end) as high_unch,
    sum(case when high < lhigh then 1 else 0 end) as high_lower,
    sum(case when low > llow then 1 else 0 end) as low_greater,
    sum(case when low = llow then 1 else 0 end) as low_unch,
    sum(case when low < llow then 1 else 0 end) as low_lower
    from obs GROUP by month ORDER by month ASC
    """, (station,))

    rows = []
    for row in cursor:
        rows.append(dict(month=row['month'],
                         increase=row["%s_greater" % (varname,)],
                         nochange=row["%s_unch" % (varname,)],
                         decrease=row["%s_lower" % (varname,)]))
    df = pd.DataFrame(rows)
    increase = np.array(df['increase'], 'f')
    nochange = np.array(df['nochange'], 'f')
    decrease = np.array(df['decrease'], 'f')

    (fig, ax) = plt.subplots(1, 1)

    total = decrease + nochange + increase

    ax.bar(np.arange(1, 13)-0.4, decrease / total * 100.0, fc='b',
           label='Decrease')
    ax.bar(np.arange(1, 13)-0.4, nochange / total * 100.0,
           bottom=(decrease/total * 100.0), fc='g', label="No Change")
    ax.bar(np.arange(1, 13)-0.4, increase / total * 100.0,
           bottom=(decrease+nochange)/total * 100.0,  fc='r',
           label="Increase")

    for i in range(1, 13):
        txt = ax.text(i, decrease[i-1] / total[i-1] * 100.0 - 5, "%.0f" % (
                            decrease[i-1] / total[i-1] * 100.0), ha='center')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="white")])
        ymid = (decrease[i-1] + (nochange[i-1]/2.)) / total[i-1] * 100.
        txt = ax.text(i, ymid, "%.0f" % (
                            nochange[i-1] / total[i-1] * 100.0),
                      ha='center', va='center')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="white")])
        txt = ax.text(i,
                      (decrease[i-1] + nochange[i-1]) / total[i-1] * 100.0 + 2,
                      "%.0f" % (increase[i-1] / total[i-1] * 100.0),
                      ha='center')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                     foreground="white")])

    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xticks(np.arange(1, 13))
    ax.legend(ncol=3)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylabel("Percentage of Days [%]")
    ax.set_title(("%s [%s]\nDay to Day %s Temperature Change"
                  ) % (nt.sts[station]['name'], station, varname.title()))

    return fig, df
