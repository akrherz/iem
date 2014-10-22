"""
  Fall Minimum by Date
"""
import psycopg2.extras
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mpcolors
import numpy as np
import datetime
import calendar
import sys
from pyiem.network import Table as NetworkTable

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200', 
             label='Select Station:'),
        dict(type='month', name='month', default=10, 
             label='Month to Plot:'),
        dict(type='year', name='year', default=2014, 
             label='Year to Highlight:'),
    ]
    return d


def plotter( fdict ):
    """ Go """
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    month = int(fdict.get('month', 10))
    year = int(fdict.get('year', 2014))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    
    cursor.execute("""
    SELECT year,  max(high),  min(low) 
    from """+table+""" where station = %s and month = %s and 
    high is not null and low is not null GROUP by year 
    ORDER by year ASC
    """, (station, month))

    years = []
    highs = []
    lows = []    
    for row in cursor:
        years.append(row[0])
        highs.append(row[1])
        lows.append(row[2])

    idx = 0
    if year in years:
        idx = years.index(year)

    highs = np.array(highs)
    lows = np.array(lows)
    rng = highs - lows
    bins = np.linspace(min(rng)-7, max(rng)+7, 8)
    cmap = cm.get_cmap('gist_rainbow')
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    
    (fig, ax) = plt.subplots(2,1, sharex=True)
    bars = ax[0].bar(years, rng, bottom=lows, fc='b', ec='b')
    bars[idx].set_facecolor('r')
    bars[idx].set_edgecolor('r')
    ax[0].axhline(np.average(highs), lw=2, color='k', zorder=2)
    ax[0].text(years[-1]+2, np.average(highs), "%.0f" % (np.average(highs),),
               ha='left', va='center')
    ax[0].axhline(np.average(lows), lw=2, color='k', zorder=2)
    ax[0].text(years[-1]+2, np.average(lows), "%.0f" % (np.average(lows),),
               ha='left', va='center')
    ax[0].grid(True)
    ax[0].set_ylabel("Temperature $^\circ$F")
    ax[0].set_xlim(years[0]-1.5, years[-1]+1.5)
    ax[0].set_title("%s %s\n%s Temperature Range (Max High - Min Low)" % (station, 
                                        nt.sts[station]['name'], 
                                        calendar.month_name[month]))

    bars = ax[1].bar(years, rng, fc='b', ec='b', zorder=1)
    bars[idx].set_facecolor('r')
    bars[idx].set_edgecolor('r')
    ax[1].set_title("Year %s [Hi: %s Lo: %s Rng: %s] Highlighted" % (year,
                                highs[idx], lows[idx], rng[idx]),
                    color='r')
    ax[1].axhline(np.average(rng), lw=2, color='k', zorder=2)
    ax[1].text(years[-1]+2, np.average(rng), "%.0f" % (np.average(rng),),
               ha='left', va='center')
    ax[1].set_ylabel("Temperature Range $^\circ$F")
    ax[1].grid(True)
    return fig
