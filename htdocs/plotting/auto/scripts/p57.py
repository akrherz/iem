import psycopg2
import pandas as pd
from pandas.io.sql import read_sql
import numpy as np
import datetime
import calendar
from pyiem.network import Table as NetworkTable
from collections import OrderedDict

PDICT = OrderedDict([('avg_temp', 'Average Daily Temperature'),
                     ('avg_high_temp', 'Average High Temperature'),
                     ('avg_low_temp', 'Average Low Temperature'),
                     ('total_precip', 'Total Precipitation')])
PDICT2 = OrderedDict([('min', 'Minimum'),
                      ('max', 'Maximum')])


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This plot displays the record months for a
    statistic of your choice.  The current month for the current day is not
    considered for the analysis."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='select', options=PDICT, name='varname', default='avg_temp',
             label='Variable to Plot'),
        dict(type='select', options=PDICT2, name='agg', default='max',
             label='Aggregate Option')
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA2203')
    varname = fdict.get('varname', 'avg_temp')
    agg = fdict.get('agg', 'max')

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    lastday = datetime.date.today()
    lastday = lastday.replace(day=1)

    df = read_sql("""SELECT year, month, avg((high+low)/2.) as avg_temp,
      avg(high) as avg_high_temp, avg(low) as avg_low_temp,
      sum(precip) as total_precip
      from """+table+""" where station = %s and day < %s GROUP by year, month
      """, pgconn, params=(station, lastday))

    resdf = pd.DataFrame(dict(monthname=pd.Series(calendar.month_abbr[1:],
                                                  index=range(1, 13))),
                         index=pd.Series(range(1, 13), name='month'))
    for _varname in PDICT:
        for _agg in [min, max]:
            df2 = df[[_varname, 'month', 'year']]
            df2 = df2[df[_varname] == df.groupby(
                        'month')[_varname].transform(_agg)].copy()
            df2.rename(
                columns={'year': '%s_%s_year' % (_agg.__name__, _varname),
                         _varname: '%s_%s' % (_agg.__name__, _varname)},
                inplace=True)
            df2.set_index('month', inplace=True)
            resdf = resdf.join(df2)

    # The above can end up with duplicates
    resdf = resdf.groupby(level=0)
    resdf = resdf.last()

    (fig, ax) = plt.subplots(1, 1)

    col = "%s_%s" % (agg, varname)
    ax.bar(np.arange(1, 13) - 0.4, resdf[col], fc='pink')
    for month, row in resdf.iterrows():
        if np.isnan(row[col]):
            continue
        ax.text(month, row[col],
                "%.0f\n%.2f" % (row[col+'_year'], row[col]), ha='center',
                va='bottom')
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(top=resdf[col].max()*1.2)
    ax.set_title(("[%s] %s\n%s %s [%s-%s]\n"
                  ) % (station, nt.sts[station]['name'],
                       PDICT2[agg], PDICT[varname],
                       nt.sts[station]['archive_begin'].year, lastday.year))
    ylabel = "Temperature $^\circ$F"
    if varname in ['total_precip']:
        ylabel = 'Precipitation [inch]'
    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xticks(np.arange(1, 13))

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.95])

    return fig, resdf

if __name__ == '__main__':
    plotter(dict())
