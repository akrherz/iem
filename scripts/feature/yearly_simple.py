import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select year, sum(precip) from alldata_ia where station = 'IA0000' and month in (3,4,5) GROUP by year ORDER by year ASC
""")

years = []
precip = []
for row in ccursor:
  years.append( row[0] )
  precip.append( row[1] )

import matplotlib.pyplot as plt
import numpy

precip = numpy.array(precip)
avg = numpy.average(precip)

(fig, ax) = plt.subplots(1,1)
years = numpy.array(years)
bars = ax.bar(years - 0.4, precip, fc='b', ec='b')
ax.plot([1893,2013],[avg,avg], lw=2.0, color='k', zorder=2)
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
for i, bar in enumerate(bars):
  if precip[i] >= 14:
    ax.text(years[i], precip[i]+0.1, "%s\n%.02f" % (years[i],precip[i],), ha='center') 

ax.set_xlabel("*2013 thru 29 May")
ax.set_xlim(1892.5, 2013.5)
ax.grid(True)
ax.set_ylabel("Total Precipitation [inch]")
ax.set_title("1893-2013 Iowa Areal Averaged Precip (March, April, May)")

fig.savefig('test.svg')

import iemplot
iemplot.makefeature('test')
