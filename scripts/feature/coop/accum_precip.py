import psycopg2
import numpy as np

data = np.zeros( (2015-1893, 366), 'f')

IEM = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = IEM.cursor()

cursor.execute("""SELECT year, extract(doy from day), precip from alldata_ia
    WHERE station = 'IA0000' and year > 1892 ORDER by day ASC""")

for row in cursor:
    if row[1] == 1:
        running = 0
    running += row[2]
    data[int(row[0])-1893, int(row[1])-1] = running
    data[int(row[0])-1893, -1] = data[int(row[0])-1893, -2]
    
bestc = 0
bestcyr = None
bestd = 11111110
bestdyr = None
for yr in range(1893,2014):
    d = np.average((data[2014-1893,:248] - data[yr-1893,:248])**2)
    if d < bestd:
        bestd = d
        bestdyr = yr
        print 'd', yr, d

    
    c = np.corrcoef(data[2014-1893,:248], data[yr-1893,:248])[0,1]
    if c > bestc:
        bestc = c
        bestcyr = yr
        print yr, c
    
p = np.percentile(data, [25,75], 0)
mx = np.max(data, 0)
mn = np.min(data[:-2,:], 0)
avg = np.average(data[:-2,:], 0)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(range(1,188), data[-1,:187], label='2014', color='r', lw=2, zorder=2)
ax.plot(range(1,367), data[1993-1893,:], label='1993', color='b', lw=2, zorder=2)
ax.plot(range(1,367), data[2008-1893,:], label='2008', color='g', lw=2, zorder=2)
ax.plot(range(1,367), data[2010-1893,:], label='2010', color='brown', lw=2, zorder=2)
ax.plot(range(1,367), avg, label='Average', color='k', lw=1, zorder=2)
ax.fill_between(range(1,367), mn, mx, color='tan', label='max', zorder=1)
ax.legend(loc=2)
ax.set_ylim(0, 50)
ax.set_title("IEM Estimated Iowa Areal Averaged Precip")
ax.set_ylabel("Accumulated Precipitation [inch]")
ax.set_xlabel("1893 - 7 July 2014")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1,367)
ax.grid(True)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
