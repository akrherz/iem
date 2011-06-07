import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

percentile = []

# Loop over April
for i in range(1,31):
  ccursor.execute("""
  SELECT year, avg((high+low)/2.) from alldata where stationid = 'ia0200'
  and month = 4 and sday <= '04%02i' GROUP by year ORDER by avg ASC
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

ax.bar( np.arange(1,31) -0.4, percentile )
ax.set_xlim(0.5,30.5)
ax.set_ylim(0,100)
ax.set_ylabel("Accumulated Percentile [100 = warmest]")
ax.set_xlabel("Day of April 2011")
ax.set_title("Ames Avg Temp [high+low] 1 Apr - X Apr Percentile\n2011 against years 1893-2010")
ax.set_yticks( (0,25,50,75,100) )
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
