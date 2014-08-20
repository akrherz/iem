import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import numpy as np
from pyiem import network
from scipy import stats
import calendar

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200', label='Select Station:'),
        dict(type='text', name='threshold', default='32', label='Enter Threshold Temperature:'),
    ]
    return d

def plotter( fdict ):
    """ Go """
    COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    threshold = int(fdict.get('threshold', 32))
    
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    ccursor.execute("""
     select year, 
     max(case when low < %s and month < 7 
         then extract(doy from day) else 0 end) as spring,
     min(case when low < %s and month > 6 
         then extract(doy from day) else 388 end) as fall         
    from """+table+""" where station = %s 
    GROUP by year ORDER by year ASC
    """, (threshold, threshold, station))
    years = []
    spring = []
    fall = []
    for row in ccursor:
        if row['fall'] > 366:
            continue
        years.append( row['year'] )
        spring.append( row['spring'] )
        fall.append( row['fall'])
        
    years = np.array(years)
    spring = np.array(spring)
    fall = np.array(fall)
        
    s_slp, s_int, s_r, s_p, s_err = stats.linregress(years, spring)
    f_slp, f_int, f_r, f_p, f_err = stats.linregress(years, fall)
        
    (fig, ax) = plt.subplots(1,1)
    ax.bar(years, fall-spring, bottom=spring, ec='tan', fc='tan', zorder=1)
    ax.plot(years, years * s_slp + s_int, lw=3,
            zorder=2, label=r"%.2f $\frac{days}{100y}$ R$^2$=%.2f" % (
                                                        s_slp * 100.,s_r ** 2))
    ax.plot(years, years * f_slp + f_int, lw=3,
            zorder=2, label=r"%.2f $\frac{days}{100y}$ R$^2$=%.2f" % (
                                                        f_slp * 100.,f_r ** 2))
    ax.grid(True)
    ax.set_title("[%s] %s Growing Season\nLast Spring and First Fall Dates below %s$^\circ$F" % (station,
                nt.sts[station]['name'], threshold))
    ax.legend(ncol=2, fontsize=14, labelspacing=2)
    ax.set_yticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
    ax.set_yticklabels( calendar.month_abbr[1:] )
    ax.set_ylim( min(spring) - 5, max(fall) + 40)
    ax.set_xlim( min(years)-1, max(years)+1)
    return fig
