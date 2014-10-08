"""
  Fall Minimum by Date
"""
import psycopg2.extras
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import datetime
from pyiem.network import Table as NetworkTable

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200', 
             label='Select Station:'),
        dict(type='year', name='year', default=datetime.datetime.now().year, 
             label='Year to Highlight:'),
    ]
    return d


def plotter( fdict ):
    """ Go """
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    today = datetime.date.today()
    thisyear = today.year
    year = int(fdict.get('year', thisyear))
    station = fdict.get('station', 'IA0200')
    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    
    startyear = int(nt.sts[station]['archive_begin'].year)
    lows = np.ma.ones( (thisyear-startyear+1, 366)) * 99
    
    cursor.execute("""SELECT extract(doy from day), year, low from 
        """+table+""" WHERE station = %s and low is not null and
        year >= %s""",
        (station, startyear))
    for row in cursor:
        lows[ row[1] - startyear, row[0] - 1 ] = row[2]

    lows.mask = np.where(lows == 99, True, False)
    
    doys = []
    avg = []
    p25 = []
    p2p5 = []
    p75 = []
    p97p5 = []
    mins = []
    maxs = []
    dyear = []
    idx = year - startyear
    last_doy = int(today.strftime("%j"))
    for doy in range(181,366):
        l = np.ma.min(lows[:-1,180:doy],1)
        avg.append( np.ma.average(l))
        mins.append( np.ma.min(l))
        maxs.append( np.ma.max(l))
        p = np.percentile(l, [2.5,25,75,97.5])
        p2p5.append( p[0] )
        p25.append( p[1] )
        p75.append( p[2] )
        p97p5.append( p[3] )
        doys.append( doy )
        if year == thisyear and doy > last_doy:
            continue
        dyear.append( np.ma.min(lows[idx,180:doy]))
    
    
    (fig, ax) = plt.subplots(1,1)
    
    ax.fill_between(doys, mins, maxs, color='pink', zorder=1, label='Range')
    ax.fill_between(doys, p2p5, p97p5, color='tan', zorder=2, label='95 tile')
    ax.fill_between(doys, p25, p75, color='gold', zorder=3, label='50 tile')
    a = ax.plot(doys, avg, zorder=4, color='k', lw=2, label='Average')
    ax.plot(doys[:len(dyear)], dyear, color='white', lw=3.5, zorder=5)
    b = ax.plot(doys[:len(dyear)], dyear, color='b', lw=1.5, zorder=6, 
                label='%s' % (year,))
    ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
    ax.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                         'Sep', 'Oct', 'Nov', 'Dec'))
    ax.set_xlim(200,366)
    ax.text( 205, 32.4, r'32$^\circ$F', ha='left')
    ax.set_ylabel("Minimum Temperature after 1 July $^\circ$F")
    ax.set_title("%s-%s %s %s\nMinimum Temperature after 1 July" % (startyear,
                thisyear-1, station, nt.sts[station]['name']))
    ax.axhline(32, linestyle='--', lw=1, color='k', zorder=6)
    ax.grid(True)
    
    from matplotlib.patches import Rectangle 
    r = Rectangle((0, 0), 1, 1, fc='pink') 
    r2 = Rectangle((0, 0), 1, 1, fc='tan') 
    r3 = Rectangle((0, 0), 1, 1, fc='gold') 
    
    ax.legend([r,r2, r3, a[0], b[0]], ['Range', '95$^{th}$ %tile', 
                                       '50$^{th}$ %tile', 'Average', 
                                       '%s' % (year,)])

    
    return fig
