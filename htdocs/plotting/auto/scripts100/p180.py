"""Daily Climatology"""
import datetime

from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This application plots daily climatology for
    a location or two of your choice.
    """
    desc['arguments'] = [
        dict(type='station', name='station1', default='IATDSM',
             label='Select Station:', network='IACLIMATE'),
        dict(type='station', name='station2', default='IATDSM',
             optional=True,
             label='Select Second Station (Optional):', network='IACLIMATE'),
        ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station1 = ctx['station1']
    station2 = ctx.get('station2')

    dbconn = get_dbconn('coop')

    df = read_sql("""
        SELECT valid, station, high, low from climate51 WHERE
        station = %s ORDER by valid ASC
     """, dbconn, params=(station1,), index_col='valid')
    subtitle = " 1951-%s\n[%s] %s " % (datetime.datetime.now().year, station1,
                                       ctx['_nt1'].sts[station1]['name'])
    subplots = 1
    if station2:
        df2 = read_sql("""
            SELECT valid, station, high, low from climate51 WHERE
            station = %s ORDER by valid ASC
         """, dbconn, params=(station2,), index_col='valid')
        df['station2'] = station2
        df['high2'] = df2['high']
        df['low2'] = df2['low']
        subtitle += " [%s] %s" % (station2, ctx['_nt2'].sts[station2]['name'])
        subplots = 2
    (fig, ax) = plt.subplots(subplots, 1, sharex=True, figsize=(8, 6))
    if not station2:
        ax = [ax, ]

    ax[0].plot(df.index.values, df['high'], color='r', linestyle='-',
               label='%s High' % (station1,))
    ax[0].plot(df.index.values, df['low'], color='b',
               label='%s Low' % (station1,))
    ax[0].set_ylabel(r"Temperature $^\circ\mathrm{F}$")
    ax[0].set_title("IEM Computed Daily Temperature Climatology"+subtitle)
    if station2:
        ax[0].plot(df.index.values, df['high2'], color='brown',
                   label='%s High' % (station2,))
        ax[0].plot(df.index.values, df['low2'], color='green',
                   label='%s Low' % (station2,))

        ax[1].plot(df.index.values, df['high'] - df['high2'], color='r',
                   label='High Diff %s - %s' % (station1, station2))
        ax[1].plot(df.index.values, df['low'] - df['low2'], color='b',
                   label='Low Diff')
        ax[1].set_ylabel(r"Temp Difference $^\circ\mathrm{F}$")
        ax[1].legend(fontsize=10, ncol=2, loc='best')
        ax[1].grid(True)

    ax[0].legend(fontsize=10, ncol=2, loc=8)
    ax[0].grid()
    ax[0].xaxis.set_major_locator(
                               mdates.MonthLocator(interval=1)
                               )
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))

    return fig, df


if __name__ == '__main__':
    plotter(dict())
