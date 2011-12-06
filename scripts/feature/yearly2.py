import iemdb, numpy
COOP =iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

data = []
ccursor.execute("""
select nov.year, nov.sum - oct.sum from (SELECT year, sum(precip) from alldata_ia where station = 'IA0200' and month = 11 GROUP by year) as nov JOIN (SELECT year, sum(precip) from alldata_ia where station = 'IA0200' and month = 10 GROUP by year) as oct on (oct.year = nov.year) ORDER by nov.year ASC

""")
for row in ccursor:
    data.append( float(row[1]) )
data= numpy.array(data)
avgV = numpy.average(data)
diff = [1,]
for i in range(1,len(data)):
    diff.append( (data[i] - data[i-1])  )
diff = numpy.array( diff )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar(numpy.arange(1893,2012)-0.4, data, ec='b', fc='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
#ax.plot([1893,2011], [avgV, avgV], color='k')
ax.grid(True)

ax.set_xlim(1892.5,2011.5)
#ax.set_ylim(50,85)
ax.set_title("Ames November versus October Precipitation [1893-2011]")
ax.set_ylabel("Precip Difference [inch]")
ax.set_xlabel("Year, 2011 data thru 16 Nov")
ax.text( 1940, 5, '%s/%s Years with Wetter November' % (numpy.sum(numpy.where(data>0,1,0)), len(data)))

"""
ax2 = fig.add_subplot(212)
bars = ax2.bar(numpy.arange(1893,2012)-0.4, diff * 1.0, ec='b', fc='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax2.set_xlim(1892.5,2011.5)
ax2.grid(True)
ax2.set_ylabel("YoY Change [inch]")
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
