import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

yearlymax = [0]*(2013-1879)
running = 0
lastyear = 1892
ccursor.execute("""
 SELECT foo.year, foo.sum, foo2.sum, foo3.sum from
 (SELECT year, sum(precip) from alldata_ia 
 where station = 'IA0000'
 and month in (3,4,5) and year > 1892 GROUP by year) as foo,
 (SELECT year, sum(precip) from alldata_ia 
 where station = 'IA0000'
 and month in (6,7,8) and year < 2012 GROUP by year) as foo2,
  (SELECT year, sum(precip) from alldata_ia 
 where station = 'IA0000'
 and month in (5) and year < 2012 GROUP by year) as foo3
 WHERE foo3.year = foo2.year and foo.year = foo2.year ORDER by foo.year ASC
""")
years = []
spring = []
summer = []
may = []
for row in ccursor:
    years.append( row[0] )
    spring.append( float(row[1])  )
    summer.append( float(row[2])  )
    may.append( float(row[3])  )

#yearlymax[-1] += 1

spring = numpy.array(spring)
summer = numpy.array(summer)
normal = numpy.average(spring) + numpy.average(summer)
normal2 = numpy.average(may) + numpy.average(summer)
years = numpy.array(years)

import matplotlib.pyplot as plt
import iemplot
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

fig, ax = plt.subplots(2,1, sharex=True, sharey=True)

ax[0].scatter(spring, summer)
ax[0].plot([0,normal],[normal,0], color='b', label="Average")
ax[0].plot([0,15], [numpy.average(summer), numpy.average(summer)], 
           color='g', label="Summer Average")
ax[0].set_xlim(0,15)
ax[0].set_ylim(0,30)
ax[0].plot([8.1,8.1], [0,30], color='r', label="2012")
for i in range(len(years)):
    if summer[i] > 17 or summer[i] < 5:
        ax[0].text(spring[i], summer[i]+0.5, "%s" % (years[i],))
        ax[1].text(may[i], summer[i]+0.5, "%s" % (years[i],))
#bars = ax[0].bar( years - 0.4, avgh, 
#        facecolor='red', ec='red', zorder=1)
#bars = ax[1].bar( years - 0.4, avgt, 
#        facecolor='green', ec='green', zorder=1)
#bars = ax[2].bar( years - 0.4, avgl, 
#        facecolor='blue', ec='blue', zorder=1)
#ax[0].set_xlim(1892.5, 2013)
#ax.set_xticks( numpy.arange(2006,2013) )
#ax.set_xticklabels( numpy.arange(2006,2013) )
ax[0].set_title("Iowa Preciptation Comparisons [1893-2011]")
ax[0].grid(True)
ax[1].grid(True)
#ax[2].grid(True)
ax[0].set_ylabel('Summer Prec(in) [Jun/Jul/Aug]')
ax[1].set_ylabel('Summer Prec(in) [Jun/Jul/Aug]')
ax[0].set_xlabel('Spring Precipitation (in) [Mar/Apr/May]')
#ax[1].set_ylabel('Avg Temp $^{\circ}\mathrm{F}$')
#ax[2].set_ylabel('Avg Low $^{\circ}\mathrm{F}$')
ax[1].plot([2.84,2.84], [0,30], color='r', label="2012")
ax[1].plot([0,15], [numpy.average(summer), numpy.average(summer)], 
           color='g', label="Summer Ave")
ax[1].scatter(may, summer)
ax[1].set_xlabel('May Precipitation (in)')
ax[1].plot([0,normal2],[normal2,0], color='b', label="Combined Average")
ax[1].legend(loc=1, prop=prop)
#ax.set_xlabel("* 2012 Data thru 30 May")
fig.savefig('test.ps')
iemplot.makefeature('test')
