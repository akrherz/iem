import psycopg2

PGCONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = PGCONN.cursor()

cursor.execute("""SELECT year, extract(doy from day) as doy, 
 sum(precip) OVER (ORDER by day ASC ROWS BETWEEN 14 PRECEDING and CURRENT ROW)
 from alldata_ia where station = 'IA0000' and year > 2000 ORDER by day ASC""")

data = {2011: [], 2012: [], 2013: [], 2014: []} 

for row in cursor:
    if row[0] < 2011:
        continue
    data[row[0]].append( row[2] )
    
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

(fig, ax) = plt.subplots(1,1)

ax.plot(np.arange(len(data[2011])), data[2011], zorder=2, c='b', label='2011')
ax.plot(np.arange(len(data[2012])), data[2012], zorder=2, c='g', label='2012')
ax.plot(np.arange(len(data[2013])), data[2013], zorder=2, c='r', label='2013')
ax.plot(np.arange(len(data[2014])), data[2014], zorder=2, lw=2, c='k', label='2014')

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