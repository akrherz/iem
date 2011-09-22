import iemdb
import numpy
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

mean = numpy.zeros((366,))
stddev = numpy.zeros((366,))

ccursor.execute("""
 SELECT extract(doy from day) as d, avg(high), stddev(high) from alldata_ia
 where stationid = 'ia0200' GROUP by d
""")
for row in ccursor:
    mean[ int(row[0]) - 1] = row[1]
    stddev[ int(row[0]) - 1] = row[2]
    
data = numpy.zeros((366,))
ccursor.execute("""
 SELECT extract(doy from day) as d, high from alldata_ia
 where stationid = 'ia0200' and year = 2011
""")
for row in ccursor:
    idx = (row[1] - mean[ int(row[0]) - 1]) / stddev[ int(row[0]) - 1]
    data[int(row[0]) - 1] = idx

WINDOW = 7
weightings = numpy.repeat(1.0, WINDOW) / WINDOW
trailing7 = numpy.convolve(data, weightings)[WINDOW-1:-(WINDOW-1)]

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)

bars = ax.bar( numpy.arange(1,367), data, fc='r', ec='r')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_facecolor('b')
        bar.set_edgecolor('b')

ax.plot( numpy.arange(7,367), trailing7, color='black', linewidth=2, label="7 Day Average")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(1,int(mx.DateTime.now().strftime("%j"))-1)
ax.grid(True)
ax.set_title("2011 Ames Standardized Daily High Temperature Index")
ax.set_ylabel("Std. Deviation Departure")
ax.legend()

yearlymax = []
yearlymin = []
ccursor.execute("""
select year, max(data), min(data) from (select year, (high - climate.avg) / climate.stddev as data from (SELECT year, extract(doy from day) as d, high from alldata_ia
 where stationid = 'ia0200' ) as obs, (SELECT extract(doy from day) as d, avg(high), stddev(high) from alldata_ia where stationid = 'ia0200' GROUP by d) as climate where obs.d = climate.d) as foo2 GROUP by year ORDER by year ASC
""")
for row in ccursor:
  yearlymax.append( row[1] )
  yearlymin.append( row[2] )

ax2 = fig.add_subplot(212)

ax2.bar(numpy.arange(1893,2012)-0.4, yearlymax, fc='r', ec='r')
ax2.bar(numpy.arange(1893,2012)-0.4, yearlymin, fc='b', ec='b')
ax2.set_title("Maximum and Minimum Departure Value by Year")
ax2.grid(True)
ax2.set_xlim(1892.5,2011.5)
ax2.set_ylabel("Std. Deviation Departure")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
