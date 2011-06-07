import iemdb 
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select sday, sum(case when high < 32 then 1 else 0 end), 
 sum(case when low < 32 then 1 else 0 end), count(*) from alldata where stationid = 'ia0200' and month = 3 group by sday ORDEr by sday ASC
""")
highs = []
lows = []
for row in ccursor:
  highs.append( row[1] / float(row[3]) * 100.0)
  lows.append( row[2] / float(row[3]) * 100.0)

import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar(np.arange(1,32), highs, width=0.4, facecolor='r', label='High')
ax.bar(np.arange(1,32)-0.4, lows, width=0.4, facecolor='b', label='Low')
ax.set_xticks( [1,7,14,21,28] )
ax.set_xlim(0.5,31.5)
ax.grid(True)
ax.set_ylabel("Frequency [%]")
ax.set_xlabel("Day of March")
ax.set_title("Ames Temperature below Freezing in March")
ax.legend()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
