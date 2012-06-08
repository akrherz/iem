import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
SELECT march.year, march.avg, april.avg from 
 (SELECT year, avg((high+low)/2.) from alldata_ia where 
  station = 'IA0200' and month = 3 and year > 1892 GROUP by year) as march,
 (SELECT year, avg((high+low)/2.) from alldata_ia where 
  station = 'IA0200' and month = 4 and year > 1892 GROUP by year) as april
WHERE march.year = april.year ORDER by march.year ASC
""")
march = []
april = []
years = []
for row in ccursor:
  years.append( row[0] )
  march.append( float(row[1]) )
  april.append( float(row[2]) )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Ames March & April Average Temperatures\n(1893-2012) * 2012 thru 22 April")

years = numpy.array(years)
march = numpy.array(march)
april = numpy.array(april)
ax.scatter(march[:-1], april[:-1])
ax.scatter(march[-1], april[-1], c='r')
ax.plot([10,80],[10,80], c='k')
ax.set_xlim(10,60)
ax.set_ylim(10,60)
ax.annotate("2012", xy=(march[-1], april[-1]+0.2),  xycoords='data',
                xytext=(4, 30), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=0,angleB=-90"))

ax.set_ylabel("April Average Temp $^{\circ}\mathrm{F}$")
ax.set_xlabel("March Average Temp $^{\circ}\mathrm{F}$")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
