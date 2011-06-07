
from matplotlib import pyplot as plt
import numpy
from scipy import stats

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

havgs = numpy.zeros( (31), numpy.float )
hstddev = numpy.zeros( (31), numpy.float )
lavgs = numpy.zeros( (31), numpy.float )
lstddev = numpy.zeros( (31), numpy.float )

# Load up averages and stddevs
ccursor.execute("""
 SELECT sday, avg(high), stddev(high),
 avg(low), stddev(low) from alldata WHERE
 stationid = 'ia2203' and month = 12 GROUP by sday 
 ORDER by sday ASC
""")
i = 0
for row in ccursor:
    havgs[i] = row[1]
    hstddev[i] = row[2]
    lavgs[i] = row[3]
    lstddev[i] = row[4]
    i += 1

# Load up yearly averages
hyravgs = numpy.zeros( (2011-1893), numpy.float)
lyravgs = numpy.zeros( (2011-1893), numpy.float)
ccursor.execute("""
    SELECT year, avg(high), avg(low) from alldata where
    stationid = 'ia2203' and month = 12 and
    year > 1892 and year < 2011 GROUP by year
    ORDER by year ASC
""")
i = 0
for row in ccursor:
    hyravgs[i] = row[1]
    lyravgs[i] = row[2]
    i += 1
    
# Loop over years
hhiyrcnts = numpy.zeros( (2011-1893), numpy.float)
hloyrcnts = numpy.zeros( (2011-1893), numpy.float)
lhiyrcnts = numpy.zeros( (2011-1893), numpy.float)
lloyrcnts = numpy.zeros( (2011-1893), numpy.float)
for yr in range(1893,2011):
    ccursor.execute("""
    SELECT extract(day from day), high, low from alldata
    where stationid = 'ia2203' and month = 12 and 
    year = %s ORDER by day ASC
    """, (yr,))
    
    i = 0
    for row in ccursor:
        if row[1] < (havgs[i] - (2. * hstddev[i])):
            hloyrcnts[yr-1893] += 1
        if row[1] > (havgs[i] + (2. * hstddev[i])):
            hhiyrcnts[yr-1893] += 1
        if row[2] < (lavgs[i] - (2. * lstddev[i])):
            lloyrcnts[yr-1893] += 1
        if row[2] > (lavgs[i] + (2. * lstddev[i])):
            lhiyrcnts[yr-1893] += 1
        i += 1

print havgs[29], hstddev[29] * 2
fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_ylim(-0.2, 10)
ax.scatter(hyravgs, hhiyrcnts-0.1, color='r', label='Above',marker='+')
ax.scatter(hyravgs, hloyrcnts+0.1, color='b', label='Below', marker='o', facecolor='none')
ax.scatter(hyravgs[-1], hhiyrcnts[-1]-0.1, color='g', marker='+', s=100)
ax.scatter(hyravgs[-1], hloyrcnts[-1]+0.1, color='g', marker='o', s=100, facecolor='none')

ax.plot([hyravgs[-1], hyravgs[-1]], [0,10], color='g', label='2010' )
a = numpy.average( hyravgs )
ax.plot([a, a], [0,10], color='b' )
#rects1 = ax.bar(numpy.arange(12), d1, 0.35, color='b')
#rects2 = ax.bar(numpy.arange(12)+0.35, d2, 0.35, color='r')
#ax.legend( (rects1[0], rects2[0]), ('1973-1989', '1990-2010') )
#ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
#ax.set_xticks( numpy.arange(12)+0.35)
ax.set_title("Des Moines December Average Temperature & Two $\sigma$ Days")
ax.set_ylabel("Two $\sigma$ Days")
ax.set_xlabel("Average High Temperature $^{\circ}\mathrm{F}$")

#a = 9. / 24. * 100.0
#ax.plot([0,12], [a,a], color='#000000')
ax.legend(ncol=2)
ax.grid(True)

ax = fig.add_subplot(212)
ax.set_ylim(-0.2, 10)
ax.scatter(lyravgs, lhiyrcnts-0.1, color='r', label='Above',marker='+')
ax.scatter(lyravgs, lloyrcnts+0.1, color='b', label='Below', marker='o', facecolor='none')
ax.scatter(lyravgs[-1], lhiyrcnts[-1]-0.1, color='g', marker='+', s=100)
ax.scatter(lyravgs[-1], lloyrcnts[-1]+0.1, color='g', marker='o', s=100, facecolor='none')

ax.plot([lyravgs[-1], lyravgs[-1]], [0,10], color='g', label='2010' )
a = numpy.average( lyravgs )
ax.plot([a, a], [0,10], color='b' )
#rects1 = ax.bar(numpy.arange(12), d1, 0.35, color='b')
#rects2 = ax.bar(numpy.arange(12)+0.35, d2, 0.35, color='r')
#ax.legend( (rects1[0], rects2[0]), ('1973-1989', '1990-2010') )
#ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
#ax.set_xticks( numpy.arange(12)+0.35)
#ax.set_title("Ames December Average Temperature & Two $\sigma$ Days")
ax.set_ylabel("Two $\sigma$ Days")
ax.set_xlabel("Average Low Temperature $^{\circ}\mathrm{F}$")
#a = 9. / 24. * 100.0
#ax.plot([0,12], [a,a], color='#000000')
ax.legend(ncol=2)
ax.grid(True)

fig.savefig("test.ps")
import iemplot
iemplot.makefeature('test')
