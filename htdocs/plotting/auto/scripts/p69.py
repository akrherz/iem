import psycopg2.extras
import numpy as np
from pyiem import network
import matplotlib.patheffects as PathEffects
import datetime
import pandas as pd


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """The frequency of days per year for the current
    year to date period that the high temperature was above average."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000',
             label='Select Station')
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
      WITH avgs as (
        SELECT sday, avg(high) from """ + table + """ WHERE
        station = %s GROUP by sday)

      SELECT year, sum(case when o.high > a.avg then 1 else 0 end),
      count(*) from """ + table + """ o, avgs a WHERE o.station = %s
      and o.sday = a.sday and extract(doy from day) < extract(doy from now())
      GROUP by year ORDER by year ASC
    """, (station, station))

    years = []
    data = []
    for row in ccursor:
        years.append(row['year'])
        data.append(float(row['sum']) / float(row['count']) * 100.)
    df = pd.DataFrame(dict(year=pd.Series(years),
                           freq=pd.Series(data)))
    data = np.array(data)
    years = np.array(years)

    (fig, ax) = plt.subplots(1, 1)
    avgv = np.average(data)

    colorabove = 'r'
    colorbelow = 'b'
    bars = ax.bar(years - 0.4, data, fc=colorabove, ec=colorabove)
    for i, bar in enumerate(bars):
        if data[i] < avgv:
            bar.set_facecolor(colorbelow)
            bar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color='k', zorder=2)
    txt = ax.text(years[10], avgv, "Avg: %.1f%%" % (avgv,),
                  color='yellow', fontsize=14, va='center')
    txt.set_path_effects([PathEffects.withStroke(linewidth=5,
                                                 foreground="k")])
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_xlabel("Year")
    ax.set_xlim(min(years)-1, max(years)+1)
    ax.set_ylabel("Frequency [%]")
    ax.grid(True)
    today = datetime.date.today()
    msg = ("[%s] %s %s-%s Frequency of Days above Long Term Average 1 Jan - %s"
           ) % (station, nt.sts[station]['name'],
                min(years), max(years), today.strftime("%-d %b"))
    tokens = msg.split()
    sz = len(tokens) / 2
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    return fig, df
