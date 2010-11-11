
from matplotlib import pyplot as plt
import numpy
import iemplot
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("select year, sum(precip) from alldata where stationid = 'ia0000' and month = 10 and sday < '1020' and year > 1989 GROUP by year ORDER by year ASC")
years = []
totals = []
for row in ccursor:
  years.append( row[0] )
  totals.append( row[1] )

#sixty = [2.56, 2.34, 2.18, 3.07, 2.12, 2.77]
#sixtyl = ["Spencer, 6 Apr","Esterville, 1 Aug", "Davenport, 9 Jul", "Ottumwa, 25 Jun", "Lamoni, 26 May", "Lamoni, 5 Jun"]
#onetwenty = [3.60, 2.81, 3.17, 3.15, 2.18, 3.52]
#onetwentyl = ["Spencer, 6 Apr","Esterville, 1 Aug", "Iowa City, 22 Jun", "Ottumwa, 25 Jun", "Ames, 26 May", "Ames, 31 Aug"]

fig = plt.figure()
ax = fig.add_subplot(111)

rects1 = ax.bar(numpy.arange(1990,2011)-0.33, totals, color='b')
ax.plot( [1989,2011], [1.49, 1.49], color='r', label='Average 1.49')
#rects2 = ax.bar(numpy.arange(2005,2011), onetwenty, 0.33, color='r', label=('2 hour'))
#ax.set_xticklabels( numpy.arange(1990,2011) )
ax.set_xlim(1989.66, 2010.66)
ax.legend(loc=2)

#for i in range(6):
#  label = "%s, %.2f" % (sixtyl[i], sixty[i])
#  ax.text( 2005 + i - 0.15, 0.05, label, color='white',
#                ha='center', va='bottom', rotation=90, fontsize=16)
#  label = "%s, %.2f" % (onetwentyl[i], onetwenty[i])
#  ax.text( 2005 + i + 0.17, 0.05, label, color='white',
#                ha='center', va='bottom', rotation=90, fontsize=16)
#

ax.set_ylabel("Accumulation [inch]")
ax.set_xlabel("Year")
ax.set_title("Statewide Iowa Precipitation Accumulation [1-19 October]\n(Unofficial IEM Estimates)")
ax.grid(True)
plt.savefig('test.ps')
iemplot.makefeature("test")
