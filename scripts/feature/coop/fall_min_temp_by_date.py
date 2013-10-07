'''
 Fall min temperature by given date
'''
import numpy as np
import psycopg2
import matplotlib.pyplot as plt

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

lows = np.ones( (2014-1893, 366)) * 99

cursor.execute("""SELECT extract(doy from day), year, low from alldata_ia
  WHERE station = 'IA0200'""")
for row in cursor:
    lows[ row[1] - 1893, row[0] - 1 ] = row[2]

doys = []
avg = []
p25 = []
p2p5 = []
p75 = []
p97p5 = []
mins = []
maxs = []
d2013 = []
for doy in range(181,366):
    l = np.min(lows[:-1,180:doy],1)
    avg.append( np.average(l))
    mins.append( np.min(l))
    maxs.append( np.max(l))
    p = np.percentile(l, [2.5,25,75,97.5])
    p2p5.append( p[0] )
    p25.append( p[1] )
    p75.append( p[2] )
    p97p5.append( p[3] )
    doys.append( doy )
    d2013.append( np.min(lows[-1,180:doy]))

(fig, ax) = plt.subplots(1,1)

ax.fill_between(doys, mins, maxs, color='pink', zorder=1, label='Range')
ax.fill_between(doys, p2p5, p97p5, color='tan', zorder=2, label='95 tile')
ax.fill_between(doys, p25, p75, color='gold', zorder=3, label='50 tile')
a = ax.plot(doys, avg, zorder=4, color='k', lw=2, label='Average')
b = ax.plot(doys[:100], d2013[:100], color='r', lw=2, zorder=5, label='2013')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(200,366)
ax.text( 205, 32.4, r'32$^\circ$F', ha='left')
ax.set_xlabel("*2013 thru 7 October")
ax.set_ylabel("Minimum Temperature after 1 July $^\circ$F")
ax.set_title("1893-2012 Ames Minimum Temperature after 1 July")
ax.axhline(32, linestyle='--', lw=1, color='k', zorder=6)
ax.grid(True)

from matplotlib.patches import Rectangle 
r = Rectangle((0, 0), 1, 1, fc='pink') 
r2 = Rectangle((0, 0), 1, 1, fc='tan') 
r3 = Rectangle((0, 0), 1, 1, fc='gold') 

ax.legend([r,r2, r3, a[0], b[0]], ['Range', '95$^{th}$ %tile', '50$^{th}$ %tile', 'Average', '2013'])

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
