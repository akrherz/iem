import psycopg2
import numpy as np
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

counts = np.zeros((366,), 'f')

cursor.execute("""
 SELECT year, max(extract(doy from day)) from alldata_ia
 where station = 'IA2203' and month < 8 and snow >= 0.1
 GROUP by year
""")
for row in cursor:
    counts[: int(row[1])] += 1.
    
import datetime
sts = datetime.datetime(2000,1,1)
xticks = []
xticklabels = []
for i in range(0,366,7):
    ts = sts + datetime.timedelta(days=i)
    xticks.append(i)
    xticklabels.append( ts.strftime("%-d\n%b"))
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(np.arange(1,367), counts / cursor.rowcount * 100.0, lw=2)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(50,150)
ax.grid(True)
ax.set_yticks([0,5,10,20,30,40,50,60,70,80,90,95,100])
ax.set_ylabel("Frequency [%]")
ax.set_title("1885-2013 Des Moines Frequency of\nMeasurable Snowfall after Date")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')