import iemdb
import matplotlib.patheffects as PathEffects

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select year as yr, avg((high+low)/2.0) from alldata_ia
 WHERE station = 'IA8706' and sday < '0129' GROUP by yr ORDER by yr ASC
""")

years = []
precip = []
for row in ccursor:
    years.append( row[0] )
    precip.append( float(row[1])  )


import matplotlib.pyplot as plt
import numpy

precip = numpy.array(precip)
avg = numpy.average(precip)

(fig, ax) = plt.subplots(1,1)
years = numpy.array(years)
bars = ax.bar(years - 0.4, precip, fc='r', ec='r', label='After 24 Jan')
bars[-1].set_facecolor('g')
bars[-1].set_edgecolor('g')
for i, bar in enumerate(bars):
    if precip[i] < precip[-1]:
        bar.set_facecolor('b')
        bar.set_edgecolor('b')
ax.axhline(avg, lw=2.0, color='k', zorder=2, label='Season Ave: %.1f' % (avg,))

#ax.set_xlabel("*2014 thru 23 Jan, year of spring shown")
ax.set_xlim(1892.5, 2014.5)
#ax.text(1980,2.75, "2013 second driest behind 1940", ha='center',
#  bbox=dict(facecolor='#FFFFFF'))
ax.grid(True)
#ax.legend(loc=2)
ax.set_ylabel(r"Average Temperature $^\circ$F")
ax.set_title("1893-2014 Waterloo 1-28 January Average Temperature")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
