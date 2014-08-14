import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import psycopg2.extras
import numpy as np
from scipy import stats
from pyiem import network
import matplotlib.patheffects as PathEffects
import datetime
import calendar

PDICT ={'max_high': 'Maximum High', 
                      'avg-high': 'Average High',
                      'min-high': 'Minimum High',
                      'max-low': 'Maximum Low', 
                      'avg-low': 'Average Low',
                      'min-low': 'Minimum Low',
                      'max-precip': 'Maximum Daily Precip',
                      'sum-precip': 'Total Precipitation',
    'days-high-above': 'Days with High Temp Greater Than or Equal To (threshold)',
    'days-lows-above': 'Days with Low Temp Greater Than or Equal To (threshold)',
    'days-lows-below': 'Days with Low Temp Below (threshold)',
                      }

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0000', label='Select Station'),
        dict(type='month', name='month', default='7', label='Month'),
        dict(type='select', name='type', default='max-high', label='Which metric to plot?',
             options=PDICT), 
        dict(type='text', name='threshold', default='-99', 
             label='Threshold (optional, specify when appropriate):'), 
    ]
    return d


def plotter( fdict ):
    """ Go """
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0000')
    month = int(fdict.get('month', 7))
    ptype = fdict.get('type', 'max_high')
    threshold = int(fdict.get('threshold', -99))

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
    SELECT year, 
    max(high) as "max-high", 
    min(high) as "min-high",
    avg(high) as "avg-high",
    max(low) as "max-low", 
    min(low) as "min-low",
    avg(low) as "avg-low",
    max(precip) as "max-precip",
    sum(precip) as "sum-precip",
    sum(case when high >= %s then 1 else 0 end) as "days-highs-above",
    sum(case when low >= %s then 1 else 0 end) as "days-lows-above",
    sum(case when low < %s then 1 else 0 end) as "days-lows-below"
  from """+table+"""
  where station = %s and month = %s
  GROUP by year ORDER by year ASC
    """, (threshold, threshold, threshold, station, month))
    
    years = []
    data = []
    for row in ccursor:
        years.append( int(row['year']) )
        data.append( float(row[ptype]) )
    
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
    if ptype.find('precip') == -1 and ptype.find('days') == -1:
        ax.set_ylim( min(data) - 5 , max(data) + 5)
    
    ax.set_xlabel("Year")
    ax.set_ylabel(PDICT[ptype])
    ax.grid(True)
    msg = "%s %s [%s] %s" % (
                calendar.month_name[month], nt.sts[station]['name'], station,
                PDICT[ptype])
    if ptype.find("days") == 0:
        msg += " (%s)" % (threshold,)
    tokens = msg.split()
    sz = len(tokens)/ 2
    ax.set_title(" ".join(tokens[:sz]) +"\n"+ " ".join(tokens[sz:]))
    
    return fig
