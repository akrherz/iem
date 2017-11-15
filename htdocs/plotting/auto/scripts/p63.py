"""records by year"""
import datetime

import numpy as np
import psycopg2.extras
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart plots the number of daily maximum
    high temperatures and daily minimum low temperatures set by year.  Ties
    are not included."""
    desc['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:', network='IACLIMATE')
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = get_dbconn('coop')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    syear = max(1893, nt.sts[station]['archive_begin'].year)
    eyear = datetime.datetime.now().year

    cursor.execute("""SELECT sday, year, high, low, day from """+table+"""
      where station = %s and sday != '0229'
      and year >= %s ORDER by day ASC""", (station, syear))

    hrecords = {}
    hyears = [0]*(eyear - syear + 1)
    lrecords = {}
    lyears = [0]*(eyear - syear + 1)
    expect = [0]*(eyear - syear + 1)

    # hstraight = 0
    for row in cursor:
        sday = row[0]
        year = row[1]
        high = row[2]
        low = row[3]
        if year == syear:
            hrecords[sday] = high
            lrecords[sday] = low
            continue
        if high > hrecords[sday]:
            hrecords[sday] = row['high']
            hyears[year - syear] += 1
            # hstraight += 1
            # if hstraight > 3:
            #    print hstraight, sday, row[4]
        # else:
        #     hstraight = 0
        if low < lrecords[sday]:
            lrecords[sday] = low
            lyears[year - syear] += 1

    for year in range(syear, eyear+1):
        expect[year-syear] = 365.0/float(year-syear+1)

    df = pd.DataFrame(dict(expected=pd.Series(expect),
                           highs=pd.Series(hyears),
                           lows=pd.Series(lyears),
                           year=np.arange(syear, eyear+1)))

    (fig, ax) = plt.subplots(2, 1, sharex=True, sharey=True)
    rects = ax[0].bar(np.arange(syear, eyear+1)-0.5, hyears,
                      facecolor='b', edgecolor='b')
    for i in range(len(rects)):
        if rects[i].get_height() > expect[i]:
            rects[i].set_facecolor('r')
            rects[i].set_edgecolor('r')
    ax[0].plot(np.arange(syear, eyear+1), expect, color='black',
               label="$365/n$")
    ax[0].set_ylim(0, 50)
    ax[0].set_xlim(syear, eyear+1)
    ax[0].grid(True)
    ax[0].legend()
    ax[0].set_ylabel("Records set per year")
    ax[0].set_title(("[%s] %s\nDaily Records Set Per Year"
                     "") % (station, nt.sts[station]['name']))
    ax[0].text(eyear - 50, 22, "Max High Temperature")

    rects = ax[1].bar(np.arange(syear, eyear+1)-0.5, lyears,
                      facecolor='r', edgecolor='r')
    for i in range(len(rects)):
        if rects[i].get_height() > expect[i]:
            rects[i].set_facecolor('b')
            rects[i].set_edgecolor('b')
    ax[1].plot(np.arange(syear, eyear+1), expect, color='black',
               label="$365/n$")
    ax[1].grid(True)
    ax[1].legend()
    ax[1].set_ylabel("Records set per year")
    ax[1].text(eyear-50, 22, "Min Low Temperature")

    return fig, df


if __name__ == '__main__':
    plotter(dict(station='IA6389', network='IACLIMATE'))
