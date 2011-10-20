import iemdb, numpy
COOP =iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

data = []
ccursor.execute("""
select extract(year from day + '2 months'::interval) as yr, sum(precip) from alldata_ia 
 where station = 'IA0200' and day < '2011-10-01' GROUP by yr ORDER by yr ASC
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
ax = fig.add_subplot(211)

bars = ax.bar(numpy.arange(1893,2012)-0.4, data, ec='b', fc='b')
for bar in bars:
    if bar.get_height() < avgV:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax.plot([1893,2011], [avgV, avgV], color='k')
ax.grid(True)

ax.set_xlim(1892.5,2011.5)
#ax.set_ylim(50,85)
ax.set_title("Ames Water Year Precipitation [1 Oct - 30 Sep]")
ax.set_ylabel("Precipitation [inch]")
ax.set_xlabel("Year")

ax2 = fig.add_subplot(212)
bars = ax2.bar(numpy.arange(1893,2012)-0.4, diff * 1.0, ec='b', fc='b')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax2.set_xlim(1892.5,2011.5)
ax2.grid(True)
ax2.set_ylabel("YoY Change [inch]")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
