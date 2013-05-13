import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT extract(year from day) as yr, max(p) from 
(SELECT foo.day, foo.precip + foo2.precip as p from
 (SELECT day, precip from alldata_ia where station = 'IA0000') as foo,
 (SELECT day + '1 day'::interval as d, precip from alldata_ia where station = 'IA0000') as foo2 WHERE foo.day = foo2.d) as foo3
  GROUP by yr ORDER by yr ASC""")

years = []
precip = []
for row in ccursor:
  print row
  years.append( row[0] )
  precip.append( row[1] )

import matplotlib.pyplot as plt
import numpy

(fig, ax) = plt.subplots(1,1)
years = numpy.array(years)
bars = ax.bar(years - 0.4, precip, fc='b', ec='b')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
for i, bar in enumerate(bars):
  if precip[i] > precip[-1]:
    ax.text(years[i], precip[i]+0.1, "%.0f" % (years[i],), ha='center') 

ax.set_xlabel("*2013 thru 21 April")
ax.set_xlim(1892.5, 2013.5)
ax.grid(True)
ax.set_ylabel("Maximum Precipitation [inch]")
ax.set_title("Iowa Yearly Maximum Two Day Areal Averaged Precip")

fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
