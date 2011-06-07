import iemdb
import numpy
import matplotlib.pyplot as plt
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select year, sum(precip) from alldata where stationid = 'ia0000'
 and year < 2011 GROUP by year ORDER by year ASC
""")
mt = []
for row in ccursor:
    mt.append( float(row[1]) )
    
mt = numpy.array( mt )
ma = numpy.zeros( (len(mt)-30))
for i in range(30, len(mt)):
    ma[i-30] = numpy.average( mt[i-30:i])

fig = plt.figure(figsize=(11,6))
ax = fig.add_subplot(111)

ax.bar( numpy.arange(1893,2011) - 0.4, mt, facecolor='#96A3FF', edgecolor="#96A3FF")
ax.plot( numpy.arange(1923,2011), ma, c='r', zorder=2, label='30 Year MA')

ax.set_xlim(1892.5,2011)
ax.set_title("Iowa Average Precipitation [1960-2010]")
ax.set_ylabel("Precipitation [inch]")
#ax.set_xlabel("2010 December thru 19 Dec")
ax.set_ylim(15,50)
ax.set_xlim(1959.5,2010.5)

ax.grid(True)
ax.legend(loc=2)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')