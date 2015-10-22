import psycopg2
from pyiem import network
import datetime
import pandas as pd
from pandas.io.sql import read_sql


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot produces a timeseries difference between
    daily high and low temperatures against climatology.
    """
    d['data'] = True
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station'),
        dict(type='year', name='year', default=datetime.date.today().year,
             label='Which Year:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')

    station = fdict.get('station', 'IA0000')
    year = int(fdict.get('year', datetime.date.today().year))
    nt = network.Table("%sCLIMATE" % (station[:2],))

    leapday = False
    try:
        _ = datetime.date(year, 2, 29)
        leapday = True
    except:
        pass

    cldf = read_sql("""
        SELECT valid, high as climate_high, low as climate_low
        from climate51 WHERE
        station = %s ORDER by valid ASC
        """, pgconn, params=(station,), index_col='valid')
    if not leapday:
        cldf.drop(datetime.date(2000, 2, 29))

    # Get specified years data
    table = "alldata_%s" % (station[:2],)
    obdf = read_sql("""
        SELECT day, high, low from """ + table + """ where
        station = %s and year = %s ORDER by day ASC
        """, pgconn, params=(station, year), index_col='day')

    # The cldf uses dates in the year 2000, lets move to this year
    cldf.index = cldf.index + pd.DateOffset(year=year)
    # now we can join
    df = cldf.join(obdf)
    df.index.name = 'Date'

    (fig, ax) = plt.subplots(2, 1, sharex=True)

    ax[0].plot(df.index, df.climate_high, color='r', linestyle='-',
               label='Climate High')
    ax[0].plot(df.index, df.climate_low, color='b', label='Climate Low')
    ax[0].set_ylabel(r"Temperature $^\circ\mathrm{F}$")
    ax[0].set_title("[%s] %s Climatology & %s Observations" % (
        station, nt.sts[station]['name'], year))

    ax[0].plot(df.index, df.high, color='brown',
               label='%s High' % (year,))
    ax[0].plot(df.index, df.low, color='green',
               label='%s Low' % (year,))

    ax[1].plot(df.index, df.high - df.climate_high, color='r',
               label='High Diff %s - Climate' % (year))
    ax[1].plot(df.index, df.low - df.climate_low, color='b',
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
