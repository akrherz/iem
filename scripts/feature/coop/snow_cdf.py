import numpy
import iemdb
import datetime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ccursor.execute("""
    SELECT day, snow, extract(year from day + '5 months'::interval) 
    from alldata_ia where station = 'IA2203' and 
    snow >= 0.01 and year > 1892 and day < '2012-06-01' ORDER by day ASC
    """)
precip = []
years = []
last = 0
ldate = datetime.date(1893,1,1)
for row in ccursor:
    date = row[0]
    if (date - ldate).days == 1:
        precip.append( last + row[1] )
        last = 0
        years.append( row[2] )
    else:
        if last > 0:
            precip.append( last )        
            years.append( row[2] )
        last = row[1]

    ldate = date

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

yearlybins = numpy.zeros( (2013-1893, 5), 'f')
yearlytotals = numpy.zeros( (2013-1893, 5), 'f')

for y,s in zip(years, precip):
    for i in range(0,5):
        if s >= bins[i] and s < bins[i+1]:
            yearlybins[ y - 1893, i] += 1
            yearlytotals[ y - 1893, i] += s
            continue

normal = 33.78
avgs = numpy.average(yearlybins, 0)
d2012 = yearlybins[-1,:]

bars = ax.bar( numpy.arange(5)-0.4, avgs, width=0.8, fc='b', label='Average')
for i in range(len(bars)):
   ax.text(bars[i].get_x()+0.4, avgs[i] + 0.5, "%.1f" % (avgs[i],), ha='center')
   #ax.text(i, avgs[i] + 9, "%.1f%%" % (yearlytotals[-1,i] / normal * 100.0 - 20.0,), ha='center', color='r')
#bars = ax.bar( numpy.arange(5), d2012, width=0.4, fc='r', label='2012')
#for i in range(len(bars)):
#   ax.text(bars[i].get_x()+0.2, d2012[i] + 2, "%.0f" % (d2012[i],), ha='center')

ax.set_ylim(0,15)
ax.legend()
ax.set_ylabel("Events per Season")
ax.set_xlabel("Snowfall Bins [inch], split into equal 20% by snow volume (~6 inches each)")
ax.set_title("Des Moines [1893-2012] Snowfall Events Contributions\n(snowfall on consecutive days lumped together)")
ax.set_xticks( numpy.arange(0,5) )
xlabels = []
for i in range(5):
  xlabels.append( "%.2f-%.2f" % (bins[i],bins[i+1]))
ax.set_xticklabels( xlabels )

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
