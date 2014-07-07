import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

dsm = []
days = []
cursor.execute("""
 SELECT day, max_tmpf from summary_2014 s JOIN stations t on (t.iemid = s.iemid)
 WHERE t.id = 'DSM' and t.network = 'IA_ASOS' and day >= '2014-07-01'
 and day < '2014-07-07' ORDER by day ASC
""")
for row in cursor:
    days.append(row[0])
    dsm.append(row[1])

percentiles = []
for d,v in zip(days, dsm):
    ccursor.execute("""SELECT sum(case when high < %s then 1 else 0 end),
    sum(case when high >= %s then 1 else 0 end) from alldata_ia where
    station = 'IA2203' and sday = %s and year < 2014""", 
    (v, v, d.strftime("%m%d"),))
    row = ccursor.fetchone()
    print d, v, row[0], row[1]
    percentiles.append( row[0] / float(row[0]+row[1]) * 100.)
    
import matplotlib.pyplot as plt
import numpy as np

(fig, ax) = plt.subplots(1,1)

bars = ax.bar(np.arange(1,7)-0.4, percentiles, width=0.8)
for x,y in zip(range(1,7), percentiles):
    ax.text(x, y+3, "%.0f$^\circ$F\n%.0f" % (dsm[x-1], y,), ha='center')
ax.set_xlabel("1-6 July 2014")
ax.set_title("Des Moines July 2014 Daily High Temperatures + Percentile\n2014 vs 1883-2013")
ax.set_ylabel("Percentile [%] 100=warmest")
ax.grid(True)
ax.set_yticks([0,25,50,75,100])
ax.set_xlim(0.5,6.5)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
    