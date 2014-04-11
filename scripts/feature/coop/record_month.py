
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

records = [0]*12
years = [0]*12
oldrecords = [0]*12
sigmas = [0]*12
ssigmas = [0]*12
avgs = [0]*12
ccursor.execute("""
 SELECT month, stddev(avg), avg(avg) from (
  SELECT month, year, avg((high+low)/2.0) from alldata_ia where
  station = 'IA2203' GROUP by year, month
 ) as foo GROUP by month """)
for row in ccursor:
  sigmas[row[0]-1] = row[1]
  avgs[row[0]-1] = row[2]

ccursor.execute("""
 SELECT year, month, avg((high+low)/2.0) from alldata_ia where
 station = 'IA2203' GROUP by year, month ORDER by avg ASC
""")
for row in ccursor:
  idx = row[1]-1
  sigma = (row[2] - avgs[idx])/sigmas[idx]
  #if sigma > 2:
  #  print sigma, row
  if row[2] > records[row[1]-1]:
    oldrecords[row[1]-1] = records[row[1]-1]
    records[row[1]-1] = row[2]
    years[row[1]-1] = row[0]
    ssigmas[idx] = sigma
import numpy
records = numpy.array(records)
oldrecords = numpy.array(oldrecords)
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)

bars = ax.bar( numpy.arange(1,13)-0.4, records, fc='pink')
bars[2].set_facecolor('r')
for i in range(12):
  ax.text(i+1, records[i]+2, "%s" % (years[i],), ha='center')
  ax.text(i+1, records[i]-8, "%.1f" % (ssigmas[i],), ha='center')
ax.set_xlim(0.5,12.5)
ax.set_ylim(0,100)
ax.set_title("Des Moines Warmest Months (high+low)/2 [1878-2012]\nYear of maximum and its sigma departure shown")
ax.set_ylabel("Avg Temp $^{\circ}\mathrm{F}$")
ax.grid(True)
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xticks( numpy.arange(1,13))

ax2 = fig.add_subplot(212)

bars = ax2.bar( numpy.arange(1,13)-0.4, records - oldrecords, fc='pink')
bars[2].set_facecolor('r')

ax2.set_xlim(0.5,12.5)
ax2.grid(True)
ax2.set_ylabel("Distance to 2nd $^{\circ}\mathrm{F}$")
ax2.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax2.set_xticks( numpy.arange(1,13))

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
