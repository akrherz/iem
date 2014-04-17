from dateutil.easter import easter
import datetime
import numpy as np

import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""SELECT day, precip from alldata_ia where station = 'IA2203'""")
data = {}
for row in cursor:
    data[ row[0] ] = row[1]

hits = [0]*7
allhits = [0]*7
events = 0
total = 0

for yr in range(1880,2014):
    total += 1
    e = easter(yr)
    if data[e] >= 0.01:
        events += 1
    for week in range(1,8):
        ts = e + datetime.timedelta(days=(week*7))
        print yr, e, ts, week 
        if data[e] >= 0.01 and data[ts] >= 0.01:
            hits[week-1] += 1
        if data[ts] >= 0.01:
            allhits[week-1] += 1
            
hits = np.array(hits)
allhits = np.array(allhits)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(np.arange(1,8)-0.4, hits / float(events) * 100., width=0.4,
       fc='purple',
       label="Rained on Easter")
ax.bar(np.arange(1,8), allhits / float(total) * 100., width=0.4, 
       fc='lightgreen',
       label="Overall Frequency")
ax.grid(True)
ax.set_title("1880-2013 Des Moines Seven Sundays after Easter")
ax.set_xlim(0.5, 7.5)
ax.set_xlabel("Sequential Sunday following Easter")
ax.set_ylabel("Percent Years with Measurable Rainfall [%]")
ax.legend(fontsize=10)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')