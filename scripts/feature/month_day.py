import iemdb

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

lcnts = [0]*30
hcnts = [0]*30

for year in range(1893,2011):
  ccursor.execute("""
  SELECT extract(day from day), high from alldata where stationid = 'ia0200'
  and month = 4 and year = %s ORDER by high ASC
  """, (year,))
  row = ccursor.fetchone()
  low = row[1]
  lcnts[ int(row[0]) - 1] += 1
  for row in ccursor:
    if row[1] == low:
      lcnts[ int(row[0]) -1] += 1
    else:
      break

  ccursor.execute("""
  SELECT extract(day from day), high from alldata where stationid = 'ia0200'
  and month = 4 and year = %s ORDER by high DESC
  """, (year,))
  row = ccursor.fetchone()
  low = row[1]
  hcnts[ int(row[0]) - 1] += 1
  for row in ccursor:
    if row[1] == low:
      hcnts[ int(row[0]) -1] += 1
    else:
      break


import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar(np.arange(1,31)-0.4, lcnts, width=0.3, facecolor='b', label='Coldest')
ax.bar(np.arange(1,31), hcnts, width=0.3, facecolor='r', label='Warmest')
ax.legend(loc=2,ncol=2)
ax.set_title("Warmest and Coolest April Daily High Temperature\nAmes [1893-2010]")
ax.set_ylabel("Occurences, ties included")
ax.set_xlabel("Day of Month")
ax.set_xlim(0.5,30.5)
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test') 
