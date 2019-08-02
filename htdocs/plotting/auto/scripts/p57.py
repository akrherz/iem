"""monthly temp records"""
import datetime
import calendar
from collections import OrderedDict

import pandas as pd
from pandas.io.sql import read_sql
import numpy as np
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict([('avg_temp', 'Average Daily Temperature'),
                     ('avg_high_temp', 'Average High Temperature'),
                     ('avg_low_temp', 'Average Low Temperature'),
                     ('total_precip', 'Total Precipitation')])
PDICT2 = OrderedDict([('min', 'Minimum'),
                      ('max', 'Maximum')])


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This plot displays the record months for a
    statistic of your choice.  The current month for the current day is not
    considered for the analysis."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             network='IACLIMATE', label='Select Station:'),
        dict(type='select', options=PDICT, name='varname', default='avg_temp',
             label='Variable to Plot'),
        dict(type='select', options=PDICT2, name='agg', default='max',
             label='Aggregate Option')
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx['station']
    varname = ctx['varname']
    agg = ctx['agg']

    table = "alldata_%s" % (station[:2],)

    lastday = datetime.date.today()
    if varname == 'total_precip' and agg == 'max':
        lastday += datetime.timedelta(days=1)
    else:
        lastday = lastday.replace(day=1)

    df = read_sql("""SELECT year, month, avg((high+low)/2.) as avg_temp,
      avg(high) as avg_high_temp, avg(low) as avg_low_temp,
      sum(precip) as total_precip
      from """+table+""" where station = %s and day < %s GROUP by year, month
      """, pgconn, params=(station, lastday))
    if df.empty:
        raise NoDataFound("No Data Found.")

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

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    col = "%s_%s" % (agg, varname)
    ax.bar(np.arange(1, 13), resdf[col], fc='pink', align='center')
    for month, row in resdf.iterrows():
        if np.isnan(row[col]):
            continue
        ax.text(month, row[col],
                "%.0f\n%.2f" % (row[col+'_year'], row[col]), ha='center',
                va='bottom')
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(top=resdf[col].max()*1.2)
    ab = ctx['_nt'].sts[station]['archive_begin']
    if ab is None:
        raise NoDataFound("Unknown Station Metadata.")
    ax.set_title(("[%s] %s\n%s %s [%s-%s]\n"
                  ) % (station, ctx['_nt'].sts[station]['name'],
                       PDICT2[agg], PDICT[varname],
                       ab.year, lastday.year))
    ylabel = r"Temperature $^\circ$F"
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
