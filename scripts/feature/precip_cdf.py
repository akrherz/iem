import numpy
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ccursor.execute("""
    SELECT precip from alldata_ia where station = 'IA2203' and precip > 0 and year > 1879
    """)
precip = []
for row in ccursor:
    precip.append( row[0] )

precip.sort()
total = sum(precip)
base = total / 5.0
onefith = total / 5.0

bins = [0]

running = 0
for p in precip:
    running += p
    if running > onefith:
       bins.append( p )
       onefith += base

bins.append( p )

yearlybins = numpy.zeros( (2013-1880, 5), 'f')
yearlytotals = numpy.zeros( (2013-1880, 5), 'f')

ccursor.execute("""
    SELECT year, precip from alldata_ia where station = 'IA2203' and precip > 0 and year > 1879
    """)
for row in ccursor:
    for i in range(0,5):
        if row[1] >= bins[i] and row[1] < bins[i+1]:
            yearlybins[ row[0] - 1880, i] += 1
            yearlytotals[ row[0] - 1880, i] += row[1]
            continue

normal = 32.26
avgs = numpy.average(yearlybins, 0)
d2012 = yearlybins[-1,:]

bars = ax.bar( numpy.arange(5)-0.4, avgs, width=0.4, fc='b', label='Average')
for i in range(len(bars)):
   ax.text(bars[i].get_x()+0.2, avgs[i] + 2, "%.1f" % (avgs[i],), ha='center')
   ax.text(i, avgs[i] + 9, "%.1f%%" % (yearlytotals[-1,i] / normal * 100.0 - 20.0,), ha='center', color='r')
bars = ax.bar( numpy.arange(5), d2012, width=0.4, fc='r', label='2012')
for i in range(len(bars)):
   ax.text(bars[i].get_x()+0.2, d2012[i] + 2, "%.0f" % (d2012[i],), ha='center')

ax.set_ylim(0,150)
ax.legend()
ax.set_ylabel("Days")
ax.set_xlabel("Precipitation Bins [inch], split into equal 20% by rain volume")
ax.set_title("Des Moines [1880-2012] Daily Precipitation Contributions")
ax.set_xticks( numpy.arange(0,5) )
xlabels = []
for i in range(5):
  xlabels.append( "%.2f-%.2f" % (bins[i],bins[i+1]))
ax.set_xticklabels( xlabels )

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
