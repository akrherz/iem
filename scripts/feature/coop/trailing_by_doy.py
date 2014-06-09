import psycopg2
import numpy as np

PGCONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = PGCONN.cursor()

cursor.execute("""SELECT year, extract(doy from day) as doy, 
 sum(precip) OVER (ORDER by day ASC ROWS BETWEEN 14 PRECEDING and CURRENT ROW)
 from alldata_ia where station = 'IA0000' and year > 1892 ORDER by day ASC""")

data = np.zeros( (2015-1893, 366), 'f')

for row in cursor:
    data[row[0]-1893, row[1]-1] = row[2]

davg = np.average(data, 0)
    
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

(fig, ax) = plt.subplots(1,1)

ax.plot(np.arange(366), davg, zorder=3, c='k', lw=2, label='Average')
ax.plot(np.arange(366), data[2011-1893,:], zorder=2, c='b', label='2011')
ax.plot(np.arange(366), data[2012-1893,:], zorder=2, c='g', label='2012')
ax.plot(np.arange(366), data[2013-1893,:], zorder=2, c='r', label='2013')
ax.plot(np.arange(366), data[2014-1893,:], zorder=2, lw=2, c='purple', label='2014')

r = Rectangle((182,0), 14, 6, fc='yellow')
ax.add_patch(r)

ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1,367)
ax.legend(ncol=2)
ax.set_title("Iowa Areal Averaged Trailing 14 Day Total Precipitation")
ax.set_ylabel("Precipitation [inch]")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')