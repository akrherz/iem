import psycopg2
from pyiem.network import Table as NetworkTable
import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
import datetime
from pyiem.datatypes import temperature
import pyiem.meteorology as pymet
from pyiem.util import get_autoplot_context
from collections import OrderedDict


PDICT = {'yes': 'Yes, Include only Year to Date period each year',
         'no': 'No, Include all available data for each year'}
VDICT = OrderedDict([
            ('tmpf', 'Air Temperature'),
            ('dwpf', 'Dew Point Temperature'),
            ('heatindex', 'Heat Index'),
            ])
LEVELS = {'tmpf': np.arange(85, 115),
          'dwpf': np.arange(60, 85),
          'heatindex': np.arange(90, 121)}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """Caution: This plot takes a bit of time to
    generate. This plot displays a histogram of hourly heat index
    values or temperature or dew point.  The connecting lines between the
    dots are to help readability."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:'),
        dict(type='year', minvalue=1973, default=datetime.date.today().year,
             name='year', label='Year to Highlight'),
        dict(type='select', options=VDICT, name='var', default='heatindex',
             label='Select variable to plot:'),
        dict(type='select', options=PDICT, name='ytd', default='no',
             label='Include Only Year to Date Data?'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    highlightyear = ctx['year']
    ytd = ctx['ytd']
    varname = ctx['var']
    nt = NetworkTable(network)
    doylimiter = ""
    if ytd == 'yes':
        doylimiter = (" and extract(doy from valid) < "
                      " extract(doy from 'TODAY'::date) ")

    df = read_sql("""
    SELECT to_char(valid, 'YYYYmmddHH24') as d, avg(tmpf)::int as tmpf,
    avg(dwpf)::int as dwpf
    from alldata WHERE station = %s and tmpf >= 50
    and dwpf <= tmpf and valid > '1973-01-01'
    and report_type = 2 """ + doylimiter + """ GROUP by d
    """, ASOS, params=(station, ), index_col=None)
    df['year'] = df['d'].apply(lambda x: int(x[:4]))

    df2 = df
    title2 = VDICT[varname]
    if varname == 'heatindex':
        title2 = "Heat Index (when accretive to air temp)"
        df['heatindex'] = df[['tmpf', 'dwpf']].apply(
            lambda x: pymet.heatindex(temperature(x[0], 'F'),
                                      temperature(x[1],
                                                  'F')).value('F'), axis=1)
        df2 = df[df['heatindex'] > df['tmpf']]

    minyear = max([1973, nt.sts[station]['archive_begin'].year])
    maxyear = datetime.date.today().year
    years = float((maxyear - minyear) + 1)
    x = []
    y = []
    y2 = []
    (fig, ax) = plt.subplots(1, 1)
    yloc = 0.9
    ax.text(0.7, 0.94, 'Avg:',
            transform=ax.transAxes, color='b')
    ax.text(0.85, 0.94, '%s:' % (highlightyear,),
            transform=ax.transAxes, color='r')
    for level in LEVELS[varname]:
        x.append(level)
        y.append(len(df2[df2[varname] >= level]) / years)
        y2.append(len(df[np.logical_and(df[varname] >= level,
                                        df['year'] == highlightyear)]))
        if level % 2 == 0:
            ax.text(0.6, yloc, '%s' % (level,),
                    transform=ax.transAxes)
            ax.text(0.7, yloc, '%.1f' % (y[-1],),
                    transform=ax.transAxes, color='b')
            ax.text(0.85, yloc, '%.0f' % (y2[-1],),
                    transform=ax.transAxes, color='r')
            yloc -= 0.04
    for x0, y0, y02 in zip(x, y, y2):
        c = 'r' if y02 > y0 else 'b'
        ax.plot([x0, x0], [y0, y02], color=c)
    rdf = pd.DataFrame({'level': x, 'avg': y, 'd%s' % (highlightyear,): y2})
    x = np.array(x, dtype=np.float64)
    ax.scatter(x, y, color='b', label='Avg')
    ax.scatter(x, y2, color='r', label="%s" % (highlightyear,))
    ax.grid(True)
    ymax = int(max([max(y), max(y2)]))
    ax.set_xlim(x[0] - 0.5, x[-1] + 0.5)
    dy = 24 * (int(ymax / 240) + 1)
    ax.set_yticks(range(0, ymax, dy))
    ax.set_ylim(-0.5, ymax + 5)
    ax2 = ax.twinx()
    ax2.set_ylim(-0.5, ymax + 5)
    ax2.set_yticks(range(0, ymax, dy))
    ax2.set_yticklabels(["%.0f" % (s,) for s in np.arange(0, ymax, dy) / 24])
    ax2.set_ylabel("Expressed in 24 Hour Days")
    ax.set_ylabel("Hours Per Year")
    ax.set_xlabel("%s $^\circ$F" % (VDICT[varname],))
    title = 'till %s' % (datetime.date.today().strftime("%-d %b"),)
    title = "Entire Year" if ytd == 'no' else title
    ax.set_title(("[%s] %s %s-%s\n"
                  "%s Histogram (%s)"
                  ) % (station, nt.sts[station]['name'],
                       minyear,
                       datetime.date.today().year, title2, title))
    ax.legend(loc=(0.2, 0.8), scatterpoints=1)
    return fig, rdf

if __name__ == '__main__':
    plotter(dict(ytd='yes', network='IA_ASOS', zstation='AMW'))
