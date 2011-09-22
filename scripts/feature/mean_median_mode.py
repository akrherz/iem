import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import numpy
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

data = numpy.zeros( (13,6) )
ccursor.execute("""
  select month, avg(high), mode(high), median(high), 
  avg(low), mode(low), median(low) from alldata where stationid = 'ia0200'
  GROUP by month ORDER by month ASC
""")
for row in ccursor:
  data[int(row[0])-1,:] = row[1:]
ccursor.execute("""
  select avg(high), mode(high), median(high), 
  avg(low), mode(low), median(low) from alldata where stationid = 'ia0200'
""")
row = ccursor.fetchone()
data[12,:] = row[:]

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_ylabel('High Temp $^{\circ}\mathrm{F}$')
ax.set_title("Ames [1893-2011] Daily Temperatures\nHigh Temperature")
ax.scatter(numpy.arange(1,14), data[:,0], color='b', marker='s', label='Mean')
ax.scatter(numpy.arange(1,14), data[:,2], color='r', marker='o', label="Median")
ax.scatter(numpy.arange(1,14), data[:,1], marker='+', label='Mode')
ax.set_xticks(numpy.arange(1,14))
ax.set_xlim(0.8,13.2)
ax.set_xticklabels(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','All') )

ax.legend(scatterpoints=1,prop=prop,loc=2)
ax.grid(True)

ax2 = fig.add_subplot(212)
ax2.set_ylabel('Low Temp $^{\circ}\mathrm{F}$')
ax2.set_title("Low Temperature")
ax2.scatter(numpy.arange(1,14), data[:,3], color='b', marker='s', label='Mean')
ax2.scatter(numpy.arange(1,14), data[:,5], color='r', marker='o', label="Median")
ax2.scatter(numpy.arange(1,14), data[:,4], marker='+', label='Mode')
ax2.legend(scatterpoints=1,prop=prop,loc=2)
ax2.grid(True)
ax2.set_xticks(numpy.arange(1,14))
ax2.set_xlim(0.8,13.2)
ax2.set_xticklabels(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','All') )

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
