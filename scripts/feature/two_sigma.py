
import matplotlib.pyplot as plt
import numpy

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

havgs = numpy.zeros( (31), numpy.float )
hstddev = numpy.zeros( (31), numpy.float )
lavgs = numpy.zeros( (31), numpy.float )
lstddev = numpy.zeros( (31), numpy.float )

ccursor.execute("""
 SELECT day, (high - avg_high) / stddev_high from
 (SELECT * from alldata_ia where station = 'IA0200' and month = 12) as foo2
 JOIN
 (SELECT sday, avg(high) as avg_high, stddev(high) as stddev_high
 from alldata_ia WHERE station = 'IA0200' and month = 12 
 GROUP by sday) as foo ON (foo2.sday = foo.sday)
 ORDER by day ASC
""")
departures = numpy.zeros( (ccursor.rowcount), 'f')
i = 0
for row in ccursor:
    departures[i] = row[1]
    i += 1

fig = plt.figure()
ax = fig.add_subplot(111)
#ax.set_ylim(-0.2, 10)
ax.scatter(departures[:-1], departures[1:] - departures[:-1] )
ax.grid(True)

fig.savefig("test.ps")
import iemplot
iemplot.makefeature('test')
