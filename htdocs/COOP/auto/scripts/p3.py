import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import psycopg2.extras
import numpy as np
from scipy import stats
from pyiem import network
import matplotlib.patheffects as PathEffects
import datetime
import calendar

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000', label='Select Station'),
        dict(type='month', name='month', default='7', label='Month'),     
    ]
    return d

def plotter( fdict ):
    """ Go """
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    month = int(fdict.get('month', 7))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
    SELECT year, max(high) as t
  from """+table+"""
  where station = %s and month = %s
  GROUP by year ORDER by year ASC
    """, (station, month))
    
    years = []
    data = []
    for row in ccursor:
        years.append( int(row['year']) )
        data.append( float(row['t']) )
    
    data = np.array( data )
    years = np.array( years )
    
    (fig, ax) = plt.subplots(1,1)
    avgv = np.average(data)
    
    bars = ax.bar(years -0.4, data, fc='r', ec='r')
    for i, bar in enumerate(bars):
        if data[i] < avgv:
            bar.set_facecolor('b')
            bar.set_edgecolor('b')
    ax.axhline( avgv, lw=2, color='k', zorder=2)
    txt = ax.text( years[10], avgv+0.3, "Avg: %.1f" % (avgv,), color='yellow')
    txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="k")])
    ax.set_xlim(years[0] - 1, years[-1] + 1)
    ax.set_ylim( min(data) - 5 , max(data) + 5)
    
    ax.set_xlabel("Year")
    ax.set_ylabel("Maximum Daily High Temp $^\circ$F")
    ax.grid(True)
    ax.legend(fontsize=10)
    ax.set_title("%s %s [%s] Maximum Daily High Temp" % (
                calendar.month_name[month], nt.sts[station]['name'], station))
    
    return fig
