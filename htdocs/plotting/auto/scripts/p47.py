"""
  Fall Minimum by Date
"""
import psycopg2.extras
import numpy as np
import calendar
import pandas as pd
from pyiem.network import Table as NetworkTable


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['data'] = True
    d['description'] = """This chart displays the combination of liquid
    precipitation with snowfall totals for a given month.  The liquid totals
    include the melted snow.  So this plot does <strong>not</strong> show
    the combination of non-frozen vs frozen precipitation."""
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203',
             label='Select Station:'),
        dict(type='month', name='month', default='12',
             label='Select Month:'),
        dict(type='year', name='year', default='2014',
             label='Select Year to Highlight:'),
    ]
    return d


def plotter(fdict):
    """ Go """
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA2203')
    month = int(fdict.get('month', 12))
    year = int(fdict.get('year', 2014))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))

    # beat month
    cursor.execute("""
    SELECT year, sum(precip), sum(snow) from """+table+"""
    WHERE station = %s and month = %s and precip >= 0
    and snow >= 0 GROUP by year ORDER by year ASC
    """, (station, month))

    precip = []
    snow = []
    years = []
    for row in cursor:
        years.append(row[0])
        precip.append(float(row[1]))
        snow.append(float(row[2]))
    df = pd.DataFrame(dict(year=pd.Series(years),
                           precip=pd.Series(precip),
                           snow=pd.Series(snow)))

    precip = np.array(precip)
    snow = np.array(snow)
    (fig, ax) = plt.subplots(1, 1)

    ax.scatter(precip, snow, s=40, marker='s', color='b', zorder=2)
    if year in years:
        ax.scatter(precip[years.index(year)], snow[years.index(year)], s=60,
                   marker='o', color='r', zorder=3, label=str(year))
    ax.set_title(("[%s] %s\n%s Snowfall vs Precipitation Totals"
                  ) % (station, nt.sts[station]['name'],
                       calendar.month_name[month]))
    ax.grid(True)
    ax.axhline(np.average(snow), lw=2, color='black')
    ax.axvline(np.average(precip), lw=2, color='black')

    ax.set_xlim(left=-0.1)
    ax.set_ylim(bottom=-0.1)
    ylim = ax.get_ylim()
    ax.text(np.average(precip), ylim[1], "%.2f" % (np.average(precip),),
            va='top', ha='center', color='white', bbox=dict(color='black'))
    xlim = ax.get_xlim()
    ax.text(xlim[1], np.average(snow),  "%.1f" % (np.average(snow),),
            va='center', ha='right', color='white', bbox=dict(color='black'))
    ax.set_ylabel("Snowfall Total [inch]")
    ax.set_xlabel("Precipitation Total (liquid + melted) [inch]")
    ax.legend(loc=2, scatterpoints=1)
    return fig, df
