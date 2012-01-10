import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

percentile = []

# Loop over April
for i in range(1,32):
  ccursor.execute("""
  SELECT year, avg((high+low)/2.) from alldata_ia where station = 'IA0200'
  and month = 12 and sday <= '12%02i' GROUP by year ORDER by avg ASC
  """ % (i,))
  cnt = 0
  for row in ccursor:
    cnt += 1
    if row[0] == 2011:
      break
  percentile.append( float(cnt) / 119.0 * 100.0 )

import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( np.arange(1,32) -0.4, percentile )
bars[-3].set_facecolor('r')
bars[-2].set_facecolor('r')
bars[-1].set_facecolor('r')
ax.set_xlim(0.5,31.5)
ax.set_ylim(0,100)
ax.set_ylabel("Accumulated Percentile [100 = warmest]")
ax.set_xlabel("Day of December 2011, last three days forecasted")
ax.set_title("Ames Avg Temp [high+low] 1 Dec - X Dec Percentile\n2011 against years 1893-2010")
ax.set_yticks( (0,25,50,75,100) )
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
