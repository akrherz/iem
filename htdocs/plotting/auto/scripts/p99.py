import psycopg2.extras
from pyiem import network
import datetime
import numpy as np


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['description'] = """This plot produces a timeseries difference between
    daily high and low temperatures against climatology.
    """
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
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    year = int(fdict.get('year', datetime.date.today().year))
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    cursor.execute(""" SELECT valid, high, low from climate51 WHERE
     station = %s ORDER by valid ASC""", (station,))
    highs = []
    lows = []
    valid = []
    valid2 = []
    highs2 = []
    lows2 = []
    for row in cursor:
        highs.append(row[1])
        lows.append(row[2])
        valid.append(row[0])

    # Get specified years data
    cursor.execute("""SELECT day, high, low from """ + table + """ where
    station = %s and year = %s ORDER by day ASC""", (station, year))

    for row in cursor:
        highs2.append(row[1])
        lows2.append(row[2])
        valid2.append(row[0].replace(year=2000))

    highs = np.array(highs)
    highs2 = np.array(highs2)
    lows = np.array(lows)
    lows2 = np.array(lows2)

    (fig, ax) = plt.subplots(2, 1, sharex=True)

    ax[0].plot(valid, highs, color='r', linestyle='-', label='Climate High')
    ax[0].plot(valid, lows, color='b', label='Climate Low')
    ax[0].set_ylabel(r"Temperature $^\circ\mathrm{F}$")
    ax[0].set_title("[%s] %s Climatology & %s Observations" % (
        station, nt.sts[station]['name'], year))

    ax[0].plot(valid2, highs2[:len(valid2)], color='brown',
               label='%s High' % (year,))
    ax[0].plot(valid2, lows2[:len(valid2)], color='green',
               label='%s Low' % (year,))

    ax[1].plot(valid[:len(highs2)], highs2 - highs[:len(highs2)], color='r',
               label='High Diff %s - Climate' % (year))
    ax[1].plot(valid[:len(lows2)], lows2 - lows[:len(lows2)], color='b',
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

    return fig
