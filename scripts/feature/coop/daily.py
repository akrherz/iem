import psycopg2
PGCONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = PGCONN.cursor()

cursor.execute("""
  SELECT sday, avg(precip), avg(case when precip > 0.005 then precip else null 
  end) from alldata_ia where station = 'IA0200' and sday != '0229'
  GROUP by sday ORDER by sday ASC
""")

days = []
avgp = []
avgp2 = []
import datetime
for row in cursor:
    ts = datetime.datetime.strptime("2001"+row[0], "%Y%m%d")
    days.append( int(ts.strftime("%j")) )
    avgp.append( row[1] )
    avgp2.append( row[2] )

import matplotlib.pyplot as plt
import numpy as np
avgp = np.array(avgp)
avgp2 = np.array(avgp2)

(fig, ax) = plt.subplots(1,1)

ax.plot(days, avgp,c='b', label='All Days')
ax.plot(days, avgp2, zorder='2', lw=2, c='r', label='Days with Precip' )
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.grid(True)
ax.legend(loc=2, ncol=1)
ax.set_title("1893-2013 Ames Daily Precipitation Averages")
ax.set_ylabel("Precipitation [inch]")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
