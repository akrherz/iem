import psycopg2
import numpy as np
import calendar
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable

PDICT = {'high': 'High temperature',
         'low': 'Low Temperature'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot displays the directional frequency of
    day to day changes in high or low temperature summarized by month."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='select', name='varname', default='high',
             label='Which metric to plot?', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as PathEffects
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0200')
    varname = fdict.get('varname', 'low')
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)

    table = "alldata_%s" % (station[:2],)

    df = read_sql("""
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
    """, pgconn, params=(station,), index_col='month')
    increase = df[varname+'_greater'].values.astype('f')
    nochange = df[varname+'_unch'].values.astype('f')
    decrease = df[varname+'_lower'].values.astype('f')

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
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylabel("Percentage of Days [%]")
    ax.set_title(("%s [%s]\nDay to Day %s Temperature Change"
                  ) % (nt.sts[station]['name'], station, varname.title()))

    return fig, df

if __name__ == '__main__':
    plotter(dict())
