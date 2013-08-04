import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
SELECT march.year, march.avg, april.avg from 
 (SELECT year, avg((high+low)/2.) from alldata_ia where 
  station = 'IA0200' and month = 7 and year > 1892 GROUP by year) as march,
 (SELECT year, avg((high+low)/2.) from alldata_ia where 
  station = 'IA0200' and month = 8 and year > 1892 GROUP by year) as april
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
ax.set_title("Ames July + August Average Temperatures (1893-2012)")

years = numpy.array(years)
march = numpy.array(march)
avgmarch = numpy.average(march)
april = numpy.array(april)
avgapril = numpy.average(april)
ax.scatter(march[:-1], april[:-1])
ax.plot([avgmarch,avgmarch], [65,85], '-.', color='r')
ax.plot([65,85], [avgapril,avgapril], '-.', color='r')
for yr,jul,aug in zip(years, march, april):
    if aug > 80 or jul < 70 or jul > 80:
        ax.text(jul,aug+0.2, "%s"% (yr,), ha='center', va='bottom')
#ax.scatter(march[-1], april[-1], c='r')
ax.plot([10,100],[10,100], c='k')
ax.set_xlim(65,85)
ax.set_ylim(65,85)
ax.annotate("2013", xy=(march[-1], 65),  xycoords='data',
                xytext=(4, 20), textcoords='offset points',
                bbox=dict(boxstyle="round", fc="0.8"),
                arrowprops=dict(arrowstyle="->",
                connectionstyle="angle3,angleA=0,angleB=-90"))

ax.set_ylabel("August Average Temp $^{\circ}\mathrm{F}$")
ax.set_xlabel("July Average Temp $^{\circ}\mathrm{F}$")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
