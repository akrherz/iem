import psycopg2
from pyiem.network import Table as NetworkTable
import datetime
import calendar
from pandas.io.sql import read_sql
from pyiem.meteorology import mixing_ratio
from pyiem.datatypes import temperature


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    today = datetime.date.today()
    d['data'] = True
    d['description'] = """This plot presents the daily mixing ratio
    climatology and observations for one year."""
    d['arguments'] = [
        dict(type='zstation', name='zstation', default='AMW',
             label='Select Station:'),
        dict(type='year', name='year', default=today.year,
             label='Select Year to Plot'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')

    station = fdict.get('zstation', 'AMW')
    network = fdict.get('network', 'IA_ASOS')
    nt = NetworkTable(network)
    year = int(fdict.get('year', 2015))

    df = read_sql("""
        SELECT extract(year from valid) as year,
        extract(doy from valid) as doy, dwpf from alldata
        where station = %s and dwpf > -50 and dwpf < 90 and
        tmpf > -50 and tmpf < 120 and valid > '1950-01-01'
    """, pgconn, params=(station,), index_col=None)
    df['mixing_ratio'] = mixing_ratio(
                            temperature(df['dwpf'].values, 'F')).value('KG/KG')
    df2 = df[['doy', 'mixing_ratio']].groupby('doy').describe()
    df2 = df2.unstack(level=-1)

    dyear = df[df['year'] == year]
    df3 = dyear[['doy', 'mixing_ratio']].groupby('doy').describe()
    df3 = df3.unstack(level=-1)
    df3['diff'] = df3[('mixing_ratio', 'mean')] - df2[('mixing_ratio', 'mean')]

    (fig, ax) = plt.subplots(2, 1)
    ax[0].fill_between(df2.index.values, df2[('mixing_ratio', 'min')] * 1000.,
                       df2[('mixing_ratio', 'max')] * 1000., color='gray')

    ax[0].plot(df2.index.values, df2[('mixing_ratio', 'mean')] * 1000.,
               label="Climatology")
    ax[0].plot(df3.index.values, df3[('mixing_ratio', 'mean')] * 1000.,
               color='r', label="%s" % (year, ))

    ax[0].set_title(("%s [%s]\nDaily Mean Surface Water Vapor Mixing Ratio"
                     ) % (station, nt.sts[station]['name']))
    ax[0].set_ylabel("Mixing Ratio ($g/kg$)")
    ax[0].set_xlim(0, 366)
    # ax[0].set_ylim(0, 26.)
    ax[0].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
                      365))
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].grid(True)
    ax[0].legend(loc=2, fontsize=10)

    rects = ax[1].bar(df3.index.values, df3['diff'] * 1000.0, edgecolor='b')
    for rect in rects:
        if rect.get_y() < 0.:
            rect.set_facecolor('r')
            rect.set_edgecolor('r')
        else:
            rect.set_facecolor('b')

    ax[1].set_ylabel("%.0f Departure ($g/kg$)" % (year, ))
    ax[1].set_xlim(0, 366)
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335,
                      365))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].grid(True)
    return fig, df3

if __name__ == '__main__':
    plotter(dict())
