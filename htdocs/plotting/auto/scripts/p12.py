import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg2.extras
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203', label='Select Station:'),
        dict(type='text', name='threshold', default='90', label='Enter Threshold:')
    ]
    return d

def plotter( fdict ):
    """ Go """
    IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    threshold = int(fdict.get('threshold', 90))
    
    table = "alldata_%s" % (station[:2],)
    
    cursor.execute("""
    SELECT year, 
    max(case when high >= %s then extract(doy from day) else 0 end) as maxsday,
    sum(case when high >= %s then 1 else 0 end) as count from """+table+"""
    WHERE station = %s GROUP by year ORDER by year ASC 
    """, (threshold, threshold, station))
    years = []
    maxsday = []
    count = []
    zeros = []
    for row in cursor:
        if row['count'] == 0:
            zeros.append( row['year'])
            continue
        count.append( row['count'] )
        maxsday.append( row['maxsday'] )
        years.append( row['year'] )
        
    count = np.array(count)
    maxsday = np.array(maxsday)
        
    (fig, ax) = plt.subplots(1,1)
    ax.scatter(maxsday, count)
    ax.grid(True)
    ax.set_ylabel("Days At or Above High Temperature")
    ax.set_title("%s [%s] Days per Year at or above %s $^\circ$F\nversus Latest Date of that Temperature" % (
                nt.sts[station]['name'], station, threshold))

    ax.text(maxsday[-1]+1, count[-1], "%s" % (years[-1],), ha='left')
    xticks = []
    xticklabels = []
    for i in np.arange(min(maxsday)-5, max(maxsday)+5, 1):
        ts = datetime.datetime(2000,1,1) + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append( ts.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Date of Last Occurrence")

    ax2 = ax.twinx()
    sortvals=np.sort( maxsday )
    yvals=np.arange(len(sortvals))/float(len(sortvals))
    ax2.plot( sortvals, yvals * 100., color='r')
    ax2.set_ylabel("Accumulated Frequency [%] (red line)")
    
    avgd = datetime.datetime(2000,1,1) + datetime.timedelta(days=int(np.average(maxsday)))
    ax.text(0.1, 0.9, "%s years failed threshold\nAvg Date: %s\nAvg Count: %.1f days" % (
                len(zeros), avgd.strftime("%-d %b"), np.average(count)),
            transform=ax.transAxes, va='top')
    
    ax.set_xlim(min(maxsday)-5, max(maxsday)+5)

    idx = int( np.argmin(maxsday) )
    ax.text(maxsday[idx]+1, count[idx], "%s" % (years[idx],),
                ha='left')
    idx = int( np.argmax(maxsday) )
    ax.text(maxsday[idx]-1, count[idx], "%s" % (years[idx],),
                ha='right')
    idx = int( np.argmax(count) )
    ax.text(maxsday[idx], count[idx]+1, "%s" % (years[idx],),
                ha='center', va='bottom')

    return fig
