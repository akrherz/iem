"""
  Fall Minimum by Date
"""
import psycopg2.extras
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import datetime
from pyiem.network import Table as NetworkTable

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['arguments'] = [
        dict(type='station', name='station', default='IA0200', 
             label='Select Station:'),
    ]
    return d


def plotter( fdict ):
    """ Go """
    pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'IA0200')
    table = "alldata_%s" % (station[:2],)
    nt = NetworkTable("%sCLIMATE" % (station[:2],))
    
    cursor.execute("""
    SELECT year,  
    min(low) as min_low,
    min(case when low < 32 and month > 8 then extract(doy from day) else 999 end) as freeze,
    min(case when low < 29 and month > 8 then extract(doy from day) else 999 end) as frost
    from """+table+""" where station = %s and month > 5 
     GROUP by year ORDER by year ASC
    """, (station,))
    
    doy = []
    doy2 = []
    for row in cursor:
        if row['frost'] > 400:
            continue
        doy.append( row['freeze'])
        doy2.append( row['frost'])
    
    doy = np.array( doy )
    doy2 = np.array( doy2 )

    sts = datetime.datetime(2000,1,1)
    xticks = []
    xticklabels = []
    for i in range(min(doy), max(doy2)+1):
        ts = sts + datetime.timedelta(days=i)
        if ts.day in [1,8,15,22]:
            xticks.append(i)
            fmt = "%b %-d" if ts.day == 1 else "%-d"
            xticklabels.append(ts.strftime(fmt))

    (fig, ax) = plt.subplots(1,1)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.scatter( doy, doy2-doy)
    
    for x in xticks:
        ax.plot((x-100,x), (100,0), ':', c=('#000000'))

    ax.set_ylim(-1,max(doy2-doy)+4)
    ax.set_xlim(min(doy)-4,max(doy)+4)
    
    ax.set_title("[%s] %s\nFirst Fall Temperature Occurences" % (
                                            station, nt.sts[station]['name']))
    ax.set_ylabel("Days until first sub 29$^{\circ}\mathrm{F}$")
    ax.set_xlabel("First day of sub 32$^{\circ}\mathrm{F}$")
    
    ax.grid(True)
    
    return fig
