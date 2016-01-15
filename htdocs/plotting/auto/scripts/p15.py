import psycopg2
import numpy as np
import calendar
import datetime
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from collections import OrderedDict

PDICT = OrderedDict([
        ('high', 'High Temperature'),
        ('low', 'Low Temperature')])


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
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Year to Highlight', min=1893),
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
    year = int(fdict.get('year', datetime.date.today().year))
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)

    table = "alldata_%s" % (station[:2],)

    df = read_sql("""
    with obs as
    (select month, year, high, lag(high) OVER (ORDER by day ASC) as lhigh,
    low, lag(low) OVER (ORDER by day ASC) as llow from """ + table + """
    where station = %s)

    SELECT year, month,
    sum(case when high > lhigh then 1 else 0 end)::numeric as high_greater,
    sum(case when high = lhigh then 1 else 0 end)::numeric as high_unch,
    sum(case when high < lhigh then 1 else 0 end)::numeric as high_lower,
    sum(case when low > llow then 1 else 0 end)::numeric as low_greater,
    sum(case when low = llow then 1 else 0 end)::numeric as low_unch,
    sum(case when low < llow then 1 else 0 end)::numeric as low_lower
    from obs GROUP by year, month ORDER by year, month
    """, pgconn, params=(station,), index_col=None)
    gdf = df.groupby('month').sum()
    gyear = df[df['year'] == year].groupby('month').sum()
    increase = gdf[varname+'_greater']
    nochange = gdf[varname+'_unch']
    decrease = gdf[varname+'_lower']
    increase2 = gyear[varname+'_greater']
    nochange2 = gyear[varname+'_unch']
    decrease2 = gyear[varname+'_lower']

    (fig, ax) = plt.subplots(1, 1)

    total = decrease + nochange + increase
    total2 = decrease2 + nochange2 + increase2

    ax.bar(total.index.values - 0.4, decrease / total * 100.0, fc='b',
           label='Decrease', width=0.4)
    ax.bar(total2.index.values, decrease2 / total2 * 100.0, fc='lightblue',
           width=0.4, label="%s ''" % (year, ))
    ax.bar(total.index.values - 0.4, nochange / total * 100.0,
           bottom=(decrease/total * 100.0), fc='g', label="No Change",
           width=0.4)
    ax.bar(total2.index.values, nochange2 / total2 * 100.0,
           bottom=(decrease2/total2 * 100.0), fc='lightgreen',
           width=0.4, label="%s ''" % (year, ))
    ax.bar(total.index.values - 0.4, increase / total * 100.0,
           bottom=(decrease+nochange)/total * 100.0,  fc='r', width=0.4,
           label="Increase")
    ax.bar(total2.index.values, increase2 / total2 * 100.0,
           bottom=(decrease2+nochange2)/total2 * 100.0,  fc='pink',
           width=0.4, label="%s ''" % (year, ))

    offset = -0.2
    for _df in [gdf, gyear]:
        increase = _df[varname+'_greater']
        nochange = _df[varname+'_unch']
        decrease = _df[varname+'_lower']
        total = decrease + nochange + increase
        for i, _ in _df.iterrows():
            txt = ax.text(i + offset,
                          decrease[i] / total[i] * 100.0 - 5, "%.0f" % (
                                decrease[i] / total[i] * 100.0), ha='center',
                          fontsize=10)
            txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                         foreground="white")])
            ymid = (decrease[i] + (nochange[i]/2.)) / total[i] * 100.
            txt = ax.text(i + offset, ymid, "%.0f" % (
                                nochange[i] / total[i] * 100.0),
                          ha='center', va='center', fontsize=10)
            txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                         foreground="white")])
            txt = ax.text(i + offset,
                          (decrease[i] + nochange[i]) / total[i] * 100.0 + 2,
                          "%.0f" % (increase[i] / total[i] * 100.0),
                          ha='center', fontsize=10)
            txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                         foreground="white")])
        offset += 0.4

    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xticks(np.arange(1, 13))
    ax.legend(ncol=3, fontsize=12, loc=9)
    ax.set_xlim(0.5, 12.5)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylabel("Percentage of Days [%]")
    ax.set_xlabel(("Dark Shades are long term averages, lighter are %s "
                   "actuals") % (year,))
    ax.set_title(("%s [%s]\nDay to Day %s Temperature Change"
                  ) % (nt.sts[station]['name'], station, varname.title()))

    return fig, df

if __name__ == '__main__':
    plotter(dict())
