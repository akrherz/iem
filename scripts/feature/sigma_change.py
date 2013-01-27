
import matplotlib.pyplot as plt
import numpy

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

hits = numpy.zeros( (12), numpy.float )
years = numpy.zeros( (2013-1900))
ccursor.execute("""
select day, high, foo2.sday, avg_high, stddev_high from 
 (SELECT day, sday, high from alldata_ia where station = 'IA0200' and
  year < 2013 and year >1899) as foo2 
 JOIN
 (SELECT sday, avg(high) as avg_high, stddev(high) as stddev_high
 from alldata_ia WHERE station = 'IA0200' GROUP by sday) as foo 
 ON (foo2.sday = foo.sday)
 ORDER by day ASC
""")
sigmas = [0,0,0,0]
highs = [0,0,0,0]
print ccursor.rowcount
for row in ccursor:
    sigmas.pop()
    sigmas.insert(0, float((row[1] - row[3]) / row[4]) )
    highs.pop()
    highs.insert(0, float(row[1]) )
    if sigmas[-1] > 1 and min(sigmas[:3]) < -1:
        hits[ int(row[0].strftime("%m"))-1] += 1
        years[ row[0].year - 1900 ] += 1

(fig, ax) = plt.subplots(2,1)
ax[0].set_xlim(0.5, 12.5)
ax[0].bar( numpy.arange(1,13)-0.4, hits / 113.0, width=0.8, fc='b', ec='b')
ax[0].set_xticks( numpy.arange(1,13) )
ax[0].set_ylabel("Days per Year per Month")
ax[0].set_title("1900-2012 Ames Daily High Temperature Swings\nFrom Day with >1 $\sigma$ to day <-1 $\sigma$ within 3 days")
ax[0].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax[0].grid(True)

ax[1].bar(numpy.arange(1900,2013), years, ec='b', fc='b')
ax[1].set_ylabel("Events per year")
ax[1].set_xlim(1900,2013)
ax[1].grid(True)

fig.savefig("test.ps")
import iemplot
iemplot.makefeature('test')
