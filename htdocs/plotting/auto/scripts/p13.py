import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg2.extras
import numpy as np
import datetime
from scipy import stats
from pyiem.network import Table as NetworkTable

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA2203', label='Select Station:'),
    ]
    return d

def plotter( fdict ):
    """ Go """
    IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    network = "%sCLIMATE" % (station[:2],)
    nt = NetworkTable(network)
    
    table = "alldata_%s" % (station[:2],)
    
    cursor.execute("""
    select year, extract(doy from day) as d from 
        (select day, year, rank() OVER (PARTITION by year ORDER by avg DESC) 
        from 
            (select day, year, avg((high+low)/2.) OVER 
            (ORDER by day ASC rows 91 preceding) from """+table+""" 
            where station = %s) as foo) as foo2 where rank = 1 
            ORDER by day DESC
    """, (station,))
    years = []
    maxsday = []
    for row in cursor:
        maxsday.append( row['d'] )
        years.append( row['year'] )
        
    maxsday = np.array(maxsday)
        
    (fig, ax) = plt.subplots(1,1)
    ax.scatter(years, maxsday)
    ax.grid(True)
    ax.set_ylabel("End Date")
    ax.set_title("%s [%s] End of Summer\nEnd Date of Warmest (Avg Temp) 91 Day Period" % (
                nt.sts[station]['name'], station))

    yticks = []
    yticklabels = []
    for i in np.arange(min(maxsday)-5, max(maxsday)+5, 1):
        ts = datetime.datetime(2000,1,1) + datetime.timedelta(days=i)
        if ts.day in [1,8,15,22,29]:
            yticks.append(i)
            yticklabels.append( ts.strftime("%-d %b"))
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)

    h_slope, intercept, r_value, p_value, std_err = stats.linregress(years, maxsday)
    ax.plot(years, h_slope * np.array(years) + intercept, lw=2, color='r')


    avgd = datetime.datetime(2000,1,1) + datetime.timedelta(days=int(np.average(maxsday)))
    ax.text(0.1, 0.03, "Avg Date: %s, slope: %.2f days/century, R$^2$=%.2f" % (
            avgd.strftime("%-d %b"), h_slope * 100., r_value ** 2),
            transform=ax.transAxes, va='bottom')
    ax.set_xlim(min(years)-1, max(years)+1)
    ax.set_ylim(min(maxsday)-5, max(maxsday)+5)


    return fig
