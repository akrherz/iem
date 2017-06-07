"""Min wind chill frequency"""
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_autoplot_context


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['description'] = """This chart presents the frequency of observed
    minimum wind chill for a winter season each year over the period of
    record for the observation site."""
    desc['cache'] = 86400
    desc['arguments'] = [
        dict(type='zstation', name='zstation', default='DSM',
             label='Select Station:', network='IA_ASOS'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    cursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['zstation']
    network = ctx['network']

    nt = NetworkTable(network)

    today = datetime.datetime.now().replace(month=6, day=1)

    cursor.execute("""
        SELECT extract(year from valid + '3 months'::interval) as yr,
         min(wcht(tmpf::numeric,(sknt*1.15)::numeric))
         from alldata WHERE station = %s and sknt >= 0 and tmpf < 32
         and valid < %s GROUP by yr ORDER by yr ASC
      """, (station, today))

    mins = []
    years = []
    for row in cursor:
        years.append(int(row[0]))
        mins.append(float(row[1]))

    df = pd.DataFrame(dict(year=pd.Series(years),
                           min_windchill=pd.Series(mins)))
    mins = np.array(mins)

    ys = []
    freq = []
    sz = float(len(mins))
    for lev in range(0, -65, -1):
        freq.append(np.sum(np.where(mins <= lev, 1, 0)) / sz * 100.0)
        ys.append(lev)
    ys = np.array(ys)

    (fig, ax) = plt.subplots(2, 1, figsize=(8, 6))

    ax[0].barh(ys - 0.4, freq, ec='b', fc='b')
    ax[0].set_ylim(-60.5, 0.5)
    ax[0].set_ylabel("Minimum Wind Chill $^\circ$F")
    ax[0].set_xlabel("Winter Season Frequency [%]")
    ax[0].set_title(("[%s] %s %s-%s\n"
                     "Season Frequency of Observed Wind Chill"
                     ) % (station, nt.sts[station]['name'],
                          years[0], years[-1]))
    ax[0].set_xticks([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100])
    ax[0].grid(True)

    ax[1].bar(years, mins, fc='b', ec='b')
    ax[1].set_ylabel("Minimum Wind Chill $^\circ$F")
    ax[1].grid(True)
    ax[1].set_xlabel("Year label for spring portion of season")

    return fig, df


if __name__ == '__main__':
    plotter(dict())
