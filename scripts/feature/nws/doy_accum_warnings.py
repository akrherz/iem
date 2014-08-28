import numpy as np
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

years = 2015-2002
counts = np.zeros( (years,366), 'f')
accum = np.zeros( (years,366), 'f')

for year in range(2002,2015):
    pcursor.execute("""SELECT extract(doy from issue) as doy, 
      count(*) from
      sbw_%s WHERE phenomena in ('SV','TO') and status = 'NEW' 
      and significance = 'W' GROUP by doy ORDER by doy ASC""" % (year,))
    for row in pcursor:
        counts[year-2002, int(row[0])-1] = row[1]
        
    for i in range(366):
        accum[:,i] = np.sum(counts[:,0:i+1], 1)
      
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1, sharex=True)

for i in range(years):
    e = 366
    if i == (years-1):
        e = 240
    l = ax.plot(np.arange(1,e+1), accum[i,:e], linewidth=2, label='%s' % (2002+i,))
    ax.text(e+1, accum[i,-1], "%s" % (2002+i,), color='w', va='center',
            fontsize=10, bbox=dict(
                                    facecolor=l[0].get_color(),
                                    edgecolor=l[0].get_color() ))

ax.set_xlim(1,367)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.legend(loc=2, ncol=3, fontsize=10)
ax.set_title("NWS Severe T'Storm + Tornado (Storm Based) Warnings\nUnited States 2002-2014 (thru 27 Aug 2014)")
ax.set_ylabel("Count")

fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
