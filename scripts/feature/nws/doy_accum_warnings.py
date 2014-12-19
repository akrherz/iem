import numpy as np
import psycopg2
import math
import copy
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

years = 2015-2003
counts = np.zeros( (years,366), 'f')
accum = np.zeros( (years,366), 'f')

for year in range(2003,2015):
    pcursor.execute("""SELECT extract(doy from issue) as doy, 
      count(*) from
      sbw_%s WHERE phenomena in ('SV','TO') and status = 'NEW' 
      and significance = 'W' GROUP by doy ORDER by doy ASC""" % (year,))
    for row in pcursor:
        counts[year-2003, int(row[0])-1] = row[1]
        
    for i in range(366):
        accum[:,i] = np.sum(counts[:,0:i+1], 1)
      
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1, sharex=True)

ann = []
for i in range(years):
    e = 366
    if i == (years-1):
        e = 352
    l = ax.plot(np.arange(1,e+1), accum[i,:e], linewidth=2, label='%s' % (2003+i,))
    ann.append(
        ax.text(e+1, accum[i,-1], "%s" % (2003+i,), color='w', va='center',
            fontsize=10, bbox=dict(
                                    facecolor=l[0].get_color(),
                                    edgecolor=l[0].get_color() ))
    )
mask = np.zeros(fig.canvas.get_width_height(), bool)

fig.canvas.draw()
offsets = [-81, -54, -27, 27]

while len(ann) > 0 and len(offsets) > 0:
    print '--Relabel Iterate---, checking %s labels' % (len(ann),)
    thisoffset = offsets.pop()
    removals = []
    for a in ann:
        bbox = a.get_window_extent()
        x0 = int(bbox.x0)
        x1 = int(math.ceil(bbox.x1))
        y0 = int(bbox.y0)
        y1 = int(math.ceil(bbox.y1))
    
        s = np.s_[x0:x1+1, y0:y1+1]
        if np.any(mask[s]):
            print 'Moved label: %s pixels: %s' % (a._text, thisoffset)
            a.set_position([366+thisoffset, a._y])
        else:
            mask[s] = True
            removals.append(a)
    for rm in removals:
        ann.remove(rm)


ax.set_xlim(1,367)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.legend(loc=2, ncol=3, fontsize=10)
ax.set_title("NWS Severe T'Storm + Tornado (Storm Based) Warnings\nUnited States 2003-2014 (thru 18 Dec 2014)")
ax.set_ylabel("Count")

fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
