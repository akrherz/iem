import iemdb, numpy
COOP =iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

data = []
ccursor.execute("""
select year, sum(precip) from alldata_ia where station = 'IA0000' and sday < '0925' and month in (7,8,9) GROUP by year ORDER by year ASC
""")
for row in ccursor:
    data.append( row[1] )
data= numpy.array(data)
avgV = numpy.average(data)

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar(numpy.arange(1893,2012)-0.4, data, ec='b', fc='b')
for bar in bars:
    if bar.get_height() < avgV:
        bar.set_facecolor('r')
        bar.set_edgecolor('r')
ax.plot([1893,2011], [avgV, avgV], color='k')
ax.grid(True)

ax.set_xlim(1892.5,2011.5)
ax.set_title("Iowa Statewide Estimated Precipitation [1 Jul - 24 Sep]")
ax.set_ylabel("Precipitation [inch]")
ax.set_xlabel("Year")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')