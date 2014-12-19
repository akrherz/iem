import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import psycopg2.extras
import datetime
import numpy as np
import math
from pyiem.network import Table as NetworkTable

def get_description():
    """ Return a dict describing how to call this plotter """
    d = dict()
    d['cache'] = 86400
    d['description'] = """Count of SVR+TOR Warnings by Year."""
    d['arguments'] = [
        dict(type='networkselect', name='station', network='WFO',
             default='DMX', label='Select WFO:', all=True)
    ]
    return d


def plotter( fdict ):
    """ Go """
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    station = fdict.get('station', 'DMX')

    nt = NetworkTable('WFO')
    nt.sts['_ALL'] = {'name': 'All Offices'}
    
    if station == '_ALL':
        cursor.execute("""
            with counts as (
                select extract(year from issue) as yr, 
                extract(doy from issue) as doy, count(*) from sbw
                where status = 'NEW' and phenomena in ('SV', 'TO') 
                and significance = 'W' and issue > '2003-01-01'
                GROUP by yr, doy)  
                
            SELECT yr, doy, sum(count) OVER (PARTITION by yr ORDER by doy ASC) 
            from counts ORDER by yr ASC, doy ASC
    
          """)
        
    else:
        cursor.execute("""
            with counts as (
                select extract(year from issue) as yr, 
                extract(doy from issue) as doy, count(*) from sbw
                where status = 'NEW' and phenomena in ('SV', 'TO') 
                and significance = 'W' and wfo = %s and issue > '2003-01-01'
                GROUP by yr, doy)  
                
            SELECT yr, doy, sum(count) OVER (PARTITION by yr ORDER by doy ASC) 
            from counts ORDER by yr ASC, doy ASC
    
          """, (station,))

    data = {}
    for yr in range(2003, datetime.datetime.now().year + 1):
        data[yr] = {'doy': [], 'counts': []}
    for row in cursor:
        data[row[0]]['doy'].append(row[1])
        data[row[0]]['counts'].append(row[2])
        
    (fig, ax) = plt.subplots(1, 1)
    ann = []
    for yr in range(2003, datetime.datetime.now().year + 1):
        if len(data[yr]['doy']) < 2:
            continue
        l = ax.plot(data[yr]['doy'], data[yr]['counts'], lw=2, label=str(yr))
        ann.append(
            ax.text(data[yr]['doy'][-1]+1, data[yr]['counts'][-1], 
                    "%s" % (yr,), color='w', va='center',
                    fontsize=10, bbox=dict(
                                    facecolor=l[0].get_color(),
                                    edgecolor=l[0].get_color() ))
            )
    
    mask = np.zeros(fig.canvas.get_width_height(), bool)
    fig.canvas.draw()
    offsets = range(0,27*5, 27)

    while len(ann) > 0 and len(offsets) > 0:
        _ = offsets.pop()
        removals = []
        for a in ann:
            bbox = a.get_window_extent()
            x0 = int(bbox.x0)
            x1 = int(math.ceil(bbox.x1))
            y0 = int(bbox.y0)
            y1 = int(math.ceil(bbox.y1))
        
            s = np.s_[x0:x1+1, y0:y1+1]
            if np.any(mask[s]):
                a.set_position([a._x-27, a._y])
            else:
                mask[s] = True
                removals.append(a)
        for rm in removals:
            ann.remove(rm)
    
    ax.legend(loc=2, ncol=3, fontsize=10)
    ax.set_xlim(1,367)
    ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
    ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
    ax.grid(True)
    ax.set_ylabel("Accumulated Count")
    ax.set_title("NWS %s SVR+TOR Warning Count" % (nt.sts[station]['name'],))

    return fig
