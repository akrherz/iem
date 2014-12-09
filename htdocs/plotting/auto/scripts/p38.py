"""
  Fall Minimum by Date
"""
import psycopg2.extras
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import datetime
import calendar
import matplotlib.patheffects as PathEffects
from pyiem.network import Table as NetworkTable

def smooth(x,window_len=11,window='hanning'):

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200', 
             label='Select Station:'),
        dict(type='year', name='year', default='2014', min=1979, 
             label='Select Year to Plot:'),
    ]
    return d


def plotter( fdict ):
    """ Go """
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    year = int(fdict.get('year', 2014))

    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    
    # HRRR data seems to be a big low, so 1.1 adjust it
    cursor.execute("""
     SELECT sday, 
     sum(case when (narr_srad < (0.75 * thres) and
                    narr_srad < (0.75 * thres) and 
                    narr_srad < (0.75 * thres)) then 1 else 0 end),
     max(thres), 
     max(case when year = %s then 
         coalesce(narr_srad, merra_srad, hrrr_srad * 1.1) else 0 end) from
     
     (SELECT sday, year, merra_srad, hrrr_srad,  
     narr_srad, max(narr_srad) OVER (partition by sday) as thres,
     lag(narr_srad) OVER (ORDER by day ASC),  
     lead(narr_srad) OVER (ORDER by day ASC)
     from """+table+""" where 
     station = %s  and year > 1978) as foo
     GROUP by sday ORDER by sday ASC
    """, (year, station ))


    y = []
    y2 = []
    for row in cursor:
        y.append( row[2] )
        y2.append( row[3] )
    y = np.array(y)
    y2 = np.array(y2)

    (fig, ax) = plt.subplots(1,1)

    smoothed = smooth(y,5)
    ax.fill_between(range(1,367), 0, smoothed, color='tan', label="Max")
    bars = ax.bar(range(366), np.where(y2 > smoothed, smoothed, y2), fc='g', 
                  ec='g', label="%s" % (year,))
    ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
    ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
    ax.set_xlim(0,366)
    ax.set_title("[%s] %s Daily Solar Radiation\n1979-2013 NARR Climatology w/ %s NARR + HRRR Estimates" % (
            station, nt.sts[station]['name'], year))
    ax.legend()
    ax.grid(True)
    ax.set_ylabel("Shortwave Solar Radiation $MJ$ $d^{-1}$")

    return fig
