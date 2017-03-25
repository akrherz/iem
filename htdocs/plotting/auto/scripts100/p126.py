import psycopg2
from pyiem.network import Table as NetworkTable
import datetime
import calendar
import numpy as np
from pandas.io.sql import read_sql
from pyiem.meteorology import mixing_ratio, relh
from pyiem.datatypes import temperature
from pyiem.util import get_autoplot_context

PDICT = {'mixing_ratio': 'Mixing Ratio [g/kg]',
         'vpd': 'Vapor Pressure Deficit [hPa]'}


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    today = datetime.date.today()
    d['data'] = True
    d['description'] = """This plot presents one of two metrics indicating
    daily humidity levels as reported by a surface weather station. The
    first being mixing ratio, which is a measure of the amount of water
    vapor in the air.  The second being vapor pressure deficit, which reports
    the difference between vapor pressure and saturated vapor pressure.
    The vapor pressure calculation shown here makes no accounting for
    leaf tempeature. The saturation vapor pressure is computed by the
    Tetens formula (Buck, 1981).

    <br />On 22 June 2016, this plot was modified to display the range of
    daily averages and not the range of instantaneous observations.
    """
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:', network='IA_ASOS'),
        dict(type='year', name='year', default=today.year,
             label='Select Year to Plot'),
        dict(type='select', name='var', default='mixing_ratio',
             label='Which Humidity Variable to Compute?', options=PDICT),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']
    nt = NetworkTable(network)
    year = ctx['year']
    varname = ctx['var']
    _ = PDICT[varname]

    df = read_sql("""
        SELECT extract(year from valid) as year,
        extract(doy from valid) as doy, tmpf, dwpf from alldata
        where station = %s and dwpf > -50 and dwpf < 90 and
        tmpf > -50 and tmpf < 120 and valid > '1950-01-01'
        and report_type = 2
    """, pgconn, params=(station,), index_col=None)
    df['relh'] = relh(temperature(df['tmpf'].values, 'F'),
                      temperature(df['dwpf'].values, 'F')).value('%')
    df['tmpc'] = temperature(df['tmpf'].values, 'F').value('C')
    df['svp'] = 0.611 * np.exp(17.502 * df['tmpc'].values /
                               (240.97 + df['tmpc'].values))
    df['vpd'] = (1. - (df['relh'] / 100.)) * df['svp']
    df['mixing_ratio'] = mixing_ratio(
                            temperature(df['dwpf'].values, 'F')).value('KG/KG')

    dailymeans = df[['year', 'doy', varname]].groupby(['year', 'doy']).mean()
    dailymeans = dailymeans.reset_index()

    df2 = dailymeans[['doy', varname]].groupby('doy').describe()
    df2 = df2.unstack(level=-1)

    dyear = df[df['year'] == year]
    df3 = dyear[['doy', varname]].groupby('doy').describe()
    df3 = df3.unstack(level=-1)
    df3['diff'] = df3[(varname, 'mean')] - df2[(varname, 'mean')]

    (fig, ax) = plt.subplots(2, 1)
    multiplier = 1000. if varname == 'mixing_ratio' else 10.
    ax[0].fill_between(df2.index.values, df2[(varname, 'min')] * multiplier,
                       df2[(varname, 'max')] * multiplier, color='gray')

    ax[0].plot(df2.index.values, df2[(varname, 'mean')] * multiplier,
               label="Climatology")
    ax[0].plot(df3.index.values, df3[(varname, 'mean')] * multiplier,
               color='r', label="%s" % (year, ))

    ax[0].set_title(("%s [%s]\nDaily Mean Surface %s"
                     ) % (station, nt.sts[station]['name'],
                          PDICT[varname]))
    lbl = ("Mixing Ratio ($g/kg$)" if varname == 'mixing_ratio'
           else PDICT[varname])
    ax[0].set_ylabel(lbl)
    ax[0].set_xlim(0, 366)
    ax[0].set_ylim(bottom=0)
    ax[0].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
                      365))
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].grid(True)
    ax[0].legend(loc=2, fontsize=10)

    cabove = 'b' if varname == 'mixing_ratio' else 'r'
    cbelow = 'r' if cabove == 'b' else 'b'
    rects = ax[1].bar(df3.index.values, df3['diff'] * multiplier,
                      facecolor=cabove, edgecolor=cabove)
    for rect in rects:
        if rect.get_y() < 0.:
            rect.set_facecolor(cbelow)
            rect.set_edgecolor(cbelow)

    units = '$g/kg$' if varname == 'mixing_ratio' else 'hPa'
    ax[1].set_ylabel("%.0f Departure (%s)" % (year, units))
    ax[1].set_xlim(0, 366)
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
                      365))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].grid(True)
    return fig, df3


if __name__ == '__main__':
    plotter({'var': 'vpd'})
