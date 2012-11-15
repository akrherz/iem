import iemdb, numpy
COOP =iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT year, sum(precip) from alldata_ia where station = 'IA0000'
 and month < 10 GROUP by year ORDER by year ASC
""")
years = []
precip = []
for row in ccursor:
    years.append( row[0] )
    precip.append( row[1] )
    
years = numpy.array(years)
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

bars = ax.bar(years-0.5, precip, fc='b', ec='b')
for bar in bars:
    if bar.get_height() <= bars[-1].get_height():
        bar.set_facecolor('r')
        bar.set_edgecolor('r')

ax.set_title("January - September Iowa Precipitation [1893-2012]")
ax.set_ylabel("Precipitation [inch]")
ax.set_xlabel("* 1894 and 1988 drier than 2012")
ax.set_xlim(min(years)-1,2013)
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')